# Paint order (occlusion), and three completion bugs found while checking it

Status: **done on `C-2.0.0-pre`**, verified by `tools/paint_order_probe.py`,
`tests/test_paint_order.py`, `tests/test_create_completes.py`,
`tests/test_rotated_arrow_tip.py`, `tests/test_animation_group_timing.py`
and a full 82-scene re-render.

## 1. What Manim CE does

CE does not paint mobject by mobject. `Camera.get_mobjects_to_display` calls

```python
extract_mobject_family_members(scene.mobjects,
                               use_z_index=True,
                               only_those_with_points=True)
```

which is (manim 0.20.1, `utils/family.py`):

1. flatten every root's family in **pre-order**,
2. drop duplicates — **first occurrence wins**,
3. **stable-sort by `m.z_index`**.

`ThreeDCamera.get_mobjects_to_display` then stable-sorts *that* list by its own
camera-space depth key, so the precedence is:

| scene | order |
|-------|-------|
| 2D    | `(z_index, family pre-order)` |
| 3D    | `(depth, z_index, family pre-order)` |

`CairoRenderer.update_frame` renders `scene.mobjects` plus any
`foreground_mobjects` that are not already in it, and `Scene.add` re-appends
`foreground_mobjects` last on every add.

Two consequences that used to be wrong in RTM:

* `z_index` reorders the **whole scene**, not just an mobject's siblings —
  `manim/mobject/graph.py` hard-codes `z_index=-1` on every edge, so a `Graph`
  draws edges *under* its vertices;
* the flattened family interleaves **across roots** — a `Dot3D` sitting on a
  saddle `Surface` has to paint between the saddle's own cells.

## 2. What RTM did before

`sync` painted `scene.mobjects` top to bottom, one root at a time, and ignored
`z_index` entirely. Every `Graph` drew its edges over its vertices, the
`SetZIndex` example from manim's own docs came out inverted, and a foreground
overlay could land behind what it was supposed to cover.

## 3. What RTM does now

`sync` collects what each root would paint into a `_PaintQueue` and flushes it
afterwards (`real_time_manim/vulkan_bind.py`). The sort key is CE's own, in
CE's own precedence:

```
(camera-space depth, z_index, family pre-order, visit order)
```

* `depth` — only in a 3D scene; `depth_key` is `ThreeDCamera`'s projection of
  `get_z_index_reference_point()`, `inf` for anything `shade_in_3d=False` (so a
  2D overlay still lands on top of every shaded face);
* `z_index` — `unit_z_index`, and only when `camera.use_z_index` is on
  (`Camera(use_z_index=False)` turns CE's sort off too);
* `family pre-order` — `family_index(roots)`, built exactly the way
  `extract_mobject_family_members` builds it;
* `visit order` — ranks units the map does not know.

Roots are deduplicated first occurrence-wins, and `foreground_mobjects` are
appended the way CE's `list_update` does.

### Cost

The whole thing is a no-op unless list order and paint order can actually
differ:

```python
walk = is_3d or z_mode or overlap          # z_mode = any non-zero z_index
index = family_index(roots) if overlap else {}
```

so a scene with no `z_index`, no 3D camera and no root that is also somebody's
child keeps the original paint path: roots painted whole, in document order,
no dict build, no sort.

## 4. Three pre-existing bugs found while verifying (all reproduce on `HEAD`)

All three were confirmed in a clean `git worktree` of `HEAD` (`da91860`)
before being fixed, so none is a side effect of the paint-order work.

### 4.1 `Create(VGroup)` left the last child short of its outline

Measured stroke length of the last square against the first, after the play:

| children | HEAD | fixed |
|----------|------|-------|
| 4  | 98.9% | 100% |
| 10 | 97.3% | 100% |
| 30 | 92.0% | 100% |

Two independent halves:

1. **The container never finished.** `_run_timeline` called `finish()` (manim's
   `interpolate(1)`) only for manim's animations; RTM's own `Create` takes an
   absolute time and `ce_frame_count` is `arange`'s exclusive end, so
   `_vulkan_progress` stopped at `0.9973`. Fixed by stepping RTM animations to
   their exact end of segment (`evaluate_animation(anim, run_time)`).
2. **The split's stamps were never cleared.** While the container is below
   1.0 the sender stamps a slice onto each child (`progress * n - i`); once
   the container reached 1.0 it stopped updating them, so every later frame
   re-painted the last child at its leftover fraction — and the split
   *multiplies* the shortfall by the number of children. Fixed by
   `release_split()`, called where CE calls `finish()`: it drops a stamp only
   while it still holds the value the split wrote, so an `Uncreate` of a
   single child in the same `play()` is left alone.

### 4.2 A rotated `Arrow` killed the render

```
vulkan_shapes.py, _send_arrow_tip:
    moved = centre + np.array([d[0] * ca - d[1] * sa,
                               d[0] * sa + d[1] * ca])
ValueError: operands could not be broadcast together with shapes (3,) (2,)
```

`centre` and `d` are 3D points and only the xy part of the rotated vector was
built, so **any** arrow with a non-zero rotation raised — scene 57
(`Rotating with about_point`) is the only demo that turns an arrow, and it
failed on every frame of it. Rotating about z leaves z alone, so the rotated
offset keeps its third component.

### 4.3 `AnimationGroup` ran its children at the wrong time

`AnimationGroup.interpolate` treated its `t` as the *normalised* alpha manim
passes when a group is a child of another group, but RTM's timeline and live
paths pass **absolute seconds**. On the timeline path every child got the
group's raw `t` as its own local time, so with `lag_ratio` the children were
never staggered — all of them jumped to the same progress at once (and
finished far too early).

Fixed in `animations/animation_group.py` by treating `t` as absolute time and
discriminating the three callers:

| caller | `start_time` | `t` |
|--------|--------------|-----|
| RTM timeline (`evaluate_animation`) | `0` | seconds since the group started |
| RTM live `play()` | wall clock | wall clock |
| manim wrapper (e.g. `ChangeSpeed`) | seconds since group start | normalised alpha `0..1` — detected as `start_time > 1e6 and t < start_time` |

Each child now begins at `origin + a_start` (its scheduled slot) and is
interpolated at `origin + group_time`; manim-child animations still receive a
normalised alpha, and the normalised flag is cleared on `begin`. The group's
default `rate_func` is now `linear`, matching manim's own default in
`composition.py` (RTM had `_smooth`, which double-smoothed every group).
`Succession` had the same wrong default and got the same fix — manim's
`Succession` is `rate_func=linear` there too.

## 5. Reproducing the checks

```bash
python -X utf8 -m pytest tests -q                       # 224 passed
python -X utf8 tools/paint_order_probe.py               # 14 CE-vs-RTM cases
python -X utf8 run_all.py --force                       # 82 scenes
python -X utf8 run.py 75                                # the only set_z_index demo
```

`tools/paint_order_probe.py` instruments RTM's leaf senders, maps each painted
mobject onto the index CE would paint it at, and reports every index that goes
backwards (`missing` / `unknown` / `twice` must all be 0).
