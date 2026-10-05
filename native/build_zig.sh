#!/usr/bin/env bash
# Build vulkan_core.dll with zig cc when no MSVC / MinGW toolchain is installed.
#
# zig's bundled clang + mingw-w64 headers/libs are enough for this renderer, so
# this needs nothing but zig (and the Vulkan SDK for headers + the loader import
# lib).  build.ps1 stays the canonical MinGW build; this one keeps the DLL
# rebuildable on a bare machine.
#
#   ZIG=/path/to/zig native/build_zig.sh            # -> dist/release/vulkan_core.dll
#   ZIG=/path/to/zig native/build_zig.sh --install   # also copy into the package
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$HERE")"
# zig is a native binary: every path handed to it must be a Windows path.
win() { cygpath -m "$1" 2>/dev/null || printf '%s' "$1"; }

ZIG="${ZIG:-$(command -v zig || true)}"
if [ -z "$ZIG" ]; then
    echo "zig not found; set ZIG=/path/to/zig" >&2
    exit 1
fi

SDK="${VULKAN_SDK:-}"
if [ -n "$SDK" ]; then
    # The env var is a Windows path (backslashes); zig is a native binary, so it
    # needs forward slashes and no MSYS-style /c/ prefix.
    SDK="$(printf '%s' "$SDK" | tr '\\' '/')"
else
    SDK="$(ls -d /c/VulkanSDK/*/ 2>/dev/null | sort | tail -1 || true)"
    if [ -n "$SDK" ]; then
        SDK="$(cygpath -m "$SDK" 2>/dev/null || printf '%s' "$SDK")"
    fi
fi
SDK="${SDK%/}"
if [ -z "$SDK" ] || [ ! -d "${SDK}/Include" ]; then
    echo "Vulkan SDK headers not found (set VULKAN_SDK)" >&2
    exit 1
fi

OUTDIR="$ROOT/dist/release"
OBJDIR="$ROOT/build/zig"
mkdir -p "$OUTDIR" "$OBJDIR"
OUTDIR_W="$(win "$OUTDIR")"
OBJDIR_W="$(win "$OBJDIR")"
SRC_W="$(win "$HERE")"

SOURCES=(
    platform.c
    vulkan_init.c
    vulkan_draw.c
    vulkan_texture.c
    draw/draw_rect.c
    draw/draw_circle.c
    draw/draw_line.c
    draw/draw_ellipse.c
    draw/draw_polygon.c
    draw/draw_dashed_line.c
    draw/draw_arc.c
    draw/draw_point.c
    draw/draw_text.c
    draw/draw_bezier.c
)

FLAGS=(-c -O2 -DNDEBUG -I"${SDK}/Include")
OBJECTS=()
for src in "${SOURCES[@]}"; do
    obj="$OBJDIR_W/$(echo "$src" | tr '/' '_' | sed 's/\.c$/.o/')"
    "${ZIG}" cc "${FLAGS[@]}" -o "$obj" "$SRC_W/$src"
    OBJECTS+=("$obj")
done

"${ZIG}" cc -shared -o "$OUTDIR_W/vulkan_core.dll" "${OBJECTS[@]}" \
    -L"${SDK}/Lib" -lvulkan-1 -luser32 -lgdi32

echo "built $OUTDIR/vulkan_core.dll"

if [ "${1:-}" = "--install" ]; then
    cp "$OUTDIR/vulkan_core.dll" "$ROOT/real_time_manim/vulkan_core.dll"
    echo "installed into real_time_manim/ (the loader prefers that copy)"
fi
