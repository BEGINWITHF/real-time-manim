"""One-time scene preparation shared by every recording worker.

Frame-parallel recording (``jobs=N``) starts one process per worker, and each
worker has to build its own scene: manim mobjects, animations and updaters are
not picklable, so the constructed scene cannot be sent across processes.  What
*can* be shared is the expensive data a scene prepares: vertex arrays, meshes,
layouts, look-up tables, parsed assets.  This module gives that a name.

Two entry points, both usable from ``construct()``:

``prepared()``
    The value of ``Scene.prepare()``, computed **once** by the parent record
    and loaded from disk by every worker.  Define::

        class Film(Scene):
            @classmethod
            def prepare(cls):
                return {"terrain": build_terrain_data()}   # picklable!

            def construct(self):
                data = prepared()
                self.add(Surface(...data["terrain"]...))

    ``prepare()`` must be a pure function of the inputs (no window, no scene
    state) and its result must be picklable with the standard library: numpy
    arrays, numbers, strings, tuples, dicts and lists are fine; mobjects with
    lambdas/updaters are not.

``shared_prepare(key, builder, version=1)``
    A small on-disk cache with a cross-process lock for scenes that cannot be
    restructured around a classmethod.  The first process to ask computes; the
    others wait and load::

        world = shared_prepare("world-v3", build_world)

    Unlike ``prepared()`` this works from any process, including a direct
    ``FrameServer`` run; the record helpers point both at a per-record temp
    directory so a parallel run computes once and workers reuse it.

When neither is used, nothing changes: no directory is read, ``prepared()``
returns ``None``.
"""
from __future__ import annotations

import os
import pickle
import re
import shutil
import tempfile
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional

PREPARE_PATH_ENV = "RTM_PREPARE_PATH"
PREPARE_DIR_ENV = "RTM_PREPARE_DIR"
PREPARE_TIMEOUT_ENV = "RTM_PREPARE_TIMEOUT"

_DEFAULT_TIMEOUT = 600.0
_lock_poll = 0.02

_MISSING = object()
_loaded_path: Optional[str] = None
_loaded_value: Any = _MISSING


def _timeout() -> float:
    raw = os.environ.get(PREPARE_TIMEOUT_ENV, "").strip()
    if not raw:
        return _DEFAULT_TIMEOUT
    try:
        return max(1.0, float(raw))
    except ValueError:
        return _DEFAULT_TIMEOUT


def _cache_dir() -> str:
    """The directory shared by this record, or a stable fallback for ad-hoc use."""
    path = os.environ.get(PREPARE_DIR_ENV, "").strip()
    if path:
        os.makedirs(path, exist_ok=True)
        return path
    path = os.path.join(tempfile.gettempdir(), "rtm_prepare")
    os.makedirs(path, exist_ok=True)
    return path


def _safe_key(key: Any, version: Any) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(key)).strip("._")[:80]
    if not text:
        raise ValueError("shared_prepare: key must contain a letter or digit")
    return "%s-v%s.pkl" % (text, int(version))


def _dump(value: Any, path: str, what: str) -> None:
    tmp = "%s.tmp-%d" % (path, os.getpid())
    try:
        with open(tmp, "wb") as fh:
            pickle.dump(value, fh, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)
    except Exception as exc:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise TypeError(
            "%s returned a value that cannot be shared with worker processes "
            "(%s).  Keep only plain data (numpy arrays, numbers, strings, "
            "dicts, lists, tuples); build mobjects/animations inside "
            "construct()." % (what, exc)
        ) from exc


def _load(path: str) -> Any:
    with open(path, "rb") as fh:
        return pickle.load(fh)


def _acquire(lock_path: str, cache_path: str, timeout: float):
    """Return an open lock fd, or ``None`` when another process finished first."""
    deadline = time.monotonic() + timeout
    while True:
        if os.path.exists(cache_path):
            return None
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                age = time.time() - os.path.getmtime(lock_path)
            except OSError:
                age = 0.0
            if age > timeout:
                # The holder died or is stuck past the budget; take the lock.
                try:
                    os.unlink(lock_path)
                    continue
                except OSError:
                    pass
            if time.monotonic() > deadline:
                raise TimeoutError(
                    "shared_prepare: timed out after %.0fs waiting for %r; "
                    "another process may still be building it (set %s to wait "
                    "longer)" % (timeout, cache_path, PREPARE_TIMEOUT_ENV)
                )
            time.sleep(_lock_poll)
            continue
        try:
            os.write(fd, str(os.getpid()).encode("ascii"))
        except OSError:
            pass
        return fd


def _release(lock_path: str, fd) -> None:
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        os.unlink(lock_path)
    except OSError:
        pass


def shared_prepare(key: Any, builder: Callable[[], Any], *,
                   version: int = 1) -> Any:
    """``builder()`` once per key, shared across worker processes.

    The first process computes and atomically publishes the pickle; concurrent
    processes wait for it and load.  ``version`` invalidates an old cache: bump
    it whenever the builder's logic or inputs change.
    """
    if not callable(builder):
        raise TypeError("shared_prepare: builder must be callable")
    directory = _cache_dir()
    path = os.path.join(directory, _safe_key(key, version))

    if os.path.exists(path):
        return _load(path)

    lock = path + ".lock"
    fd = _acquire(lock, path, _timeout())
    if fd is None:
        return _load(path)
    try:
        if os.path.exists(path):          # another process won while we waited
            return _load(path)
        value = builder()
        _dump(value, path, "shared_prepare(%r)" % (key,))
        return value
    finally:
        _release(lock, fd)


def _reset_prepared_cache() -> None:
    global _loaded_path, _loaded_value
    _loaded_path = None
    _loaded_value = _MISSING


def prepared(default: Any = None) -> Any:
    """The parent's ``Scene.prepare()`` result, or ``default`` outside a record.

    Loaded once per process; every worker sees the same object.
    """
    global _loaded_path, _loaded_value
    path = os.environ.get(PREPARE_PATH_ENV, "").strip()
    if not path:
        return default
    if not os.path.exists(path):
        raise RuntimeError(
            "prepared(): %s points at %r, which does not exist; the record "
            "helper did not publish Scene.prepare()" % (PREPARE_PATH_ENV, path)
        )
    if _loaded_path != path:
        _loaded_value = _load(path)
        _loaded_path = path
    return _loaded_value


@contextmanager
def scene_prepared(scene: Any):
    """Publish ``scene.prepare()`` and a shared cache dir for one record.

    The directory lives until the recording (including all workers) finishes,
    then is removed; a previous environment is restored so nested records do
    not leak state.
    """
    previous_path = os.environ.get(PREPARE_PATH_ENV)
    previous_dir = os.environ.get(PREPARE_DIR_ENV)
    # A caller-provided directory is a persistent cache (keep it); otherwise
    # this record gets a temp dir that dies with the workers.
    created = previous_dir is None
    directory = (tempfile.mkdtemp(prefix="rtm_prepare_") if created
                 else previous_dir)
    os.makedirs(directory, exist_ok=True)
    _reset_prepared_cache()
    os.environ[PREPARE_DIR_ENV] = directory
    os.environ.pop(PREPARE_PATH_ENV, None)
    payload_path = None
    try:
        hook = getattr(scene, "prepare", None)
        if callable(hook):
            value = hook()
            payload_path = os.path.join(directory, "scene.prepare")
            _dump(value, payload_path, "Scene.prepare()")
            os.environ[PREPARE_PATH_ENV] = payload_path
        yield
    finally:
        _reset_prepared_cache()
        if previous_path is None:
            os.environ.pop(PREPARE_PATH_ENV, None)
        else:
            os.environ[PREPARE_PATH_ENV] = previous_path
        if previous_dir is None:
            os.environ.pop(PREPARE_DIR_ENV, None)
        else:
            os.environ[PREPARE_DIR_ENV] = previous_dir
        if created:
            shutil.rmtree(directory, ignore_errors=True)
        elif payload_path is not None:
            try:
                os.unlink(payload_path)
            except OSError:
                pass
