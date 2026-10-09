@echo off
REM Build real_time_manim\vulkan_core.dll with MSVC (cl.exe from VS2022 Enterprise).
REM Usage (from anywhere): cmd /c native\build_msvc.bat
setlocal
call "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
cd /d "%~dp0"
set VK="C:\VulkanSDK\1.4.350.0"
cl /nologo /LD /O2 /DNDEBUG /I%VK%\Include ^
   platform.c vulkan_init.c vulkan_draw.c vulkan_texture.c ^
   draw\draw_rect.c draw\draw_circle.c draw\draw_line.c draw\draw_ellipse.c ^
   draw\draw_polygon.c draw\draw_dashed_line.c draw\draw_arc.c draw\draw_point.c ^
   draw\draw_text.c draw\draw_bezier.c ^
   /Fe:..\real_time_manim\vulkan_core.dll ^
   /link /LIBPATH:%VK%\Lib vulkan-1.lib user32.lib gdi32.lib
echo EXITCODE=%ERRORLEVEL%
