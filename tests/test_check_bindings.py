"""The native parameter-binding checker must find every defect it claims to.

`tools/check_bindings.py` diffs three things -- the C exports under `native/`,
the ctypes `argtypes`/`restype` declarations, and every `<dll>.<fn>(...)` call
site -- and reports 忘绑 (a missing binding), 绑反 (arguments in the wrong
order), a short list, a wrong type, a missing `byref`, a missing export and a
header/implementation disagreement.

A checker nobody has ever seen fail is a checker that cannot be trusted, so its
detection claims are executed against fixtures: 14 miniature projects, each
containing exactly one defect (plus one clean project that must stay silent).
Run the same thing by hand with::

    python tools/check_bindings.py --selftest

and the real tree with::

    python tools/check_bindings.py [--info] [--dump]
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.check_bindings import (
    SELFTEST_CASES,
    check,
    python_roots,
    scan_native,
    scan_python,
    selftest,
)


def test_every_detector_fires():
    assert selftest(verbose=False), "a check_bindings detector stopped firing"


def test_the_selftest_table_is_not_empty():
    # the table is the specification of what the checker can detect
    assert len(SELFTEST_CASES) >= 12
    assert len({c[0] for c in SELFTEST_CASES}) == len(SELFTEST_CASES)


@pytest.mark.parametrize("code", [
    "ARG_COUNT_MISMATCH",
    "ARGTYPES_MISMATCH",
    "ARGTYPES_SWAPPED",
    "BINDING_CONFLICT",
    "BINDING_TARGET_MISSING",
    "CALL_ARITY",
    "CALL_BYREF",
    "CALL_SWAPPED",
    "C_PARAM_MISMATCH",
    "UNBOUND_ARGTYPES",
    "UNBOUND_RESTYPE",
])
def test_the_checker_covers_the_reported_defect_classes(code):
    covered = {c[1] for c in SELFTEST_CASES}
    assert code in covered


def test_the_real_tree_has_no_binding_error():
    """CI gate: the repository's own bindings must stay consistent."""
    exports = scan_native()
    paths = python_roots(False)
    bindings, calls, _aliases = scan_python(paths)
    errors = [f for f in check(exports, bindings, calls)
              if f.severity == "ERROR"]
    assert not errors, "\n".join(
        "%s %s %s: %s" % (f.severity, f.code, f.symbol, f.message)
        for f in errors)
