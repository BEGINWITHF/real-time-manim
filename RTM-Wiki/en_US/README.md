# RTM-Wiki (English manual)

An English manual snapshot for Real-Time-Manim (RTM): **122 pages**, 9 chapters, **351** sample clips.

Every API gets its own section, each with a sample video; the parameter tables spell out "what you may pass / what you should not / why it has no effect".

## Layout

```
RTM-Wiki/
├─ README.md              ← this file (overview)
└─ en_US/
   ├─ 00-Getting-Started/           5 pages   installation, first scene, live window, recording, frame preview
   ├─ 01-Scenes-and-Cameras/       17 pages   scene lifecycle, play, special scenes, cameras, config
   ├─ 02-Mobjects/                 16 pages   construction and containers, positioning, measurement, transforms, style, copying, updaters
   ├─ 03-Animations/               32 pages   creation/removal, fades, transforms, emphasis, growth, movement/rotation, composition, text and numbers
   ├─ 04-Shapes-and-Text/          23 pages   geometry, lines and arrows, polygons, annotations, booleans, styles, Text/LaTeX/Typst/matrices/tables/images
   ├─ 05-Coordinates-and-Plots/    14 pages   number line, Axes, conversion, grids, curves, areas, polar, BarChart, ticks
   ├─ 06-Three-Dimensional/         5 pages   3D primitives, surfaces, polyhedra, utilities
   ├─ 07-Graphs-and-Vector-Fields/  4 pages   Graph/DiGraph, vector fields, streamlines
   └─ 08-Utilities/                 6 pages   colours, rate functions, direction constants, vector and geometry utilities
```

Inside a chapter:

```
<chapter>/README.md             the chapter index (page list + each page's sample clip and source entry point)
<chapter>/<page>.md             the page (title + intro + one section per function: signature / parameter table / sample code / video / notes)
<chapter>/assets/RTM output/    the chapter's sample clips (the mp4s embedded in the pages)
<chapter>/assets/RTM code/      the demo scripts that produce those clips (the page code blocks match them word for word)
```

## How to read

1. Start with the chapter's `README.md`, then click into the pages you need;
2. Every page has a fixed shape: **one section per function (or group of parameters)**, containing a signature, a parameter table, complete sample code, a sample video and optional notes;
3. In the parameter tables: `accepted` = usable values; `not recommended` = usable but avoid; `not wired / unwired` = RTM will not read it (the description gives the alternative);
4. The video only demonstrates the parameter's effect — the parameter table and the "what this code does" text are the authority.

## How to produce the samples

The sample scripts depend only on RTM itself (`fast_record_scene` renders offline, no window needed):

```powershell
# one page: render every sample on the page and concatenate them into the page's video (written to assets/RTM output/)
python "...\RTM-Wiki\en_US\04-Shapes-and-Text\assets\RTM code\12-Numbers-and-Variables.py"

# render a single sample
python "...\RTM-Wiki\en_US\04-Shapes-and-Text\assets\RTM code\12-Numbers-and-Variables.py" decimal
```

- Output is fixed at **1920×1080@60** (a script that writes `MLWindow(960, 540)` is corrected and prints a notice; that is expected);
- Running a script needs `PYTHONPATH` pointing at the real-time-manim repository root (or run from inside that repository);
- Every page's `<video>` lives under `assets/RTM output/`, named `<page>-<sample>.mp4`.
