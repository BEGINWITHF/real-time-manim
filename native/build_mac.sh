#!/bin/bash
# build_mac.sh — build the manim Vulkan renderer as a macOS dylib.
# Equivalent of build.ps1 on Windows; outputs dist/release/vulkan_core.dylib.
set -e
cd "$(dirname "$0")"

BUILD_CONFIG="${1:-release}"
PROJECT_ROOT="$(cd .. && pwd)"
OBJDIR="$PROJECT_ROOT/build/$BUILD_CONFIG-mac"
OUTDIR="$PROJECT_ROOT/dist/$BUILD_CONFIG"
OUT="$OUTDIR/vulkan_core.dylib"

if [ "$BUILD_CONFIG" = "debug" ]; then
    OPT="-O0 -g -DDEBUG"
else
    OPT="-O2 -DNDEBUG"
fi

# Header search order: SDK Vulkan headers (MoltenVK layer headers) and
# Homebrew (vulkan-headers).
INC_PATHS=()
if [ -d "$HOME/VulkanSDK" ]; then
    SDK_INC="$(ls -d "$HOME"/VulkanSDK/*/macOS/include 2>/dev/null | sort -V | tail -1)"
    if [ -n "$SDK_INC" ]; then
        INC_PATHS+=("$SDK_INC")
    fi
fi
INC_PATHS+=("/opt/homebrew/include")

MOLTENVK_DIR=""
for d in "$HOME/VulkanSDK"/1*/macOS/lib /opt/homebrew/opt/molten-vk/lib; do
    if [ -f "$d/libMoltenVK.dylib" ] || [ -f "$d/MoltenVK.xcframework" ]; then
        MOLTENVK_DIR="$d"
        break
    fi
done
if [ -z "$MOLTENVK_DIR" ]; then
    echo "[ERROR] libMoltenVK.dylib not found (brew install molten-vk)" >&2
    exit 1
fi

# -fdeclspec makes the Windows __declspec(dllexport) declarations in
# platform.h / draw/*.c parse on clang WITHOUT touching the Windows sources
# (clang ignores the attribute on non-Windows targets — silence the warning).
# Default visibility exports every non-static symbol, so no export macro is
# needed on the definitions either.
CFLAGS=(-fdeclspec -fvisibility=default -Wno-ignored-attributes $OPT -std=c11)
for p in "${INC_PATHS[@]}"; do
    CFLAGS+=("-I$p")
done

mkdir -p "$OBJDIR" "$OUTDIR"

echo "========================================"
echo " Manim Vulkan Native Build (macOS)"
echo "========================================"
echo "Configuration: $BUILD_CONFIG"
echo "Vulkan headers: ${INC_PATHS[*]}"
echo "MoltenVK:       $MOLTENVK_DIR"
echo "========================================"

SOURCES=(
    "vulkan_init.c"
    "vulkan_draw.c"
    "vulkan_texture.c"
    "draw/draw_rect.c"
    "draw/draw_circle.c"
    "draw/draw_line.c"
    "draw/draw_ellipse.c"
    "draw/draw_polygon.c"
    "draw/draw_dashed_line.c"
    "draw/draw_arc.c"
    "draw/draw_point.c"
    "draw/draw_text.c"
    "draw/draw_bezier.c"
)
OBJS=()
for src in "${SOURCES[@]}"; do
    if [ ! -f "$src" ]; then
        echo "[ERROR] Source file not found: $src" >&2
        exit 1
    fi
    obj="$OBJDIR/${src//\//_}.o"
    OBJS+=("$obj")
    echo "[CMD] clang -c $src"
    clang "${CFLAGS[@]}" -c "$src" -o "$obj"
done

# platform_mac.m — Objective-C (Cocoa + Metal window layer).
echo "[CMD] clang -c platform_mac.m"
clang "${CFLAGS[@]}" -c platform_mac.m -o "$OBJDIR/platform_mac.o"
OBJS+=("$OBJDIR/platform_mac.o")

echo "[INFO] Linking $OUT ..."
clang -dynamiclib -o "$OUT" "${OBJS[@]}" \
    -L"$MOLTENVK_DIR" -lMoltenVK \
    -framework Cocoa -framework Metal -framework QuartzCore \
    -Wl,-rpath,"$MOLTENVK_DIR"

echo "[SUCCESS] Compilation successful!"
echo "[INFO] Output: $OUT"
