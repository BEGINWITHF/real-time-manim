Set-Location $PSScriptRoot

$BuildConfig = if ($args.Count -gt 0 -and $args[0] -eq "debug") { "debug" } else { "release" }
$Version = "1.0.0"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$BuildDir = Join-Path $ProjectRoot "build"
$DistDir = Join-Path $ProjectRoot "dist"
$ObjDir = Join-Path $BuildDir $BuildConfig
$OutputDir = Join-Path $DistDir $BuildConfig

New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
New-Item -ItemType Directory -Force -Path $ObjDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Manim Vulkan Native Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration: $BuildConfig" -ForegroundColor Yellow
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

$vulkanBase = "C:\VulkanSDK"
if (Test-Path $vulkanBase) {
    $latestVersion = Get-ChildItem -Path $vulkanBase -Directory | 
                     Where-Object { $_.Name -match '^\d+(\.\d+){2,3}$' } | 
                     Sort-Object Name -Descending | 
                     Select-Object -First 1
    
    if ($latestVersion) {
        $env:VULKAN_SDK = $latestVersion.FullName
        Write-Host "[SUCCESS] Vulkan SDK: $env:VULKAN_SDK" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] No valid SDK version found under $vulkanBase" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[WARNING] Vulkan SDK not found at $vulkanBase" -ForegroundColor Yellow
    $download = Read-Host "Download and install Vulkan SDK now? (Y/n)"
    if ($download -eq 'n' -or $download -eq 'N') {
        Write-Host "[ERROR] Vulkan SDK is required. Exiting." -ForegroundColor Red
        exit 1
    }

    Write-Host "[INFO] Downloading Vulkan SDK installer..." -ForegroundColor Cyan
    $sdkUrl = "https://sdk.lunarg.com/sdk/download/latest/windows/vulkan-sdk.exe"
    $installerPath = Join-Path $env:TEMP "vulkan-sdk-installer.exe"

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $sdkUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "[SUCCESS] Downloaded installer to $installerPath" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download Vulkan SDK: $_" -ForegroundColor Red
        exit 1
    }

    Write-Host "[INFO] Running Vulkan SDK installer (silent mode)..." -ForegroundColor Cyan
    Write-Host "[INFO] A UAC prompt may appear - please approve it." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "--accept-licenses", "--default-answer", "yes", "--confirm-command", "install" -Wait -NoNewWindow

    if (!(Test-Path $vulkanBase)) {
        Write-Host "[ERROR] Installation completed but SDK still not found at $vulkanBase" -ForegroundColor Red
        Write-Host "[INFO] Try running the installer manually: $installerPath" -ForegroundColor Yellow
        exit 1
    }

    $latestVersion = Get-ChildItem -Path $vulkanBase -Directory | 
                     Where-Object { $_.Name -match '^\d+(\.\d+){2,3}$' } | 
                     Sort-Object Name -Descending | 
                     Select-Object -First 1
    
    if ($latestVersion) {
        $env:VULKAN_SDK = $latestVersion.FullName
        Write-Host "[SUCCESS] Vulkan SDK installed: $env:VULKAN_SDK" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] No valid SDK version found under $vulkanBase after install" -ForegroundColor Red
        exit 1
    }
}

# Check for GCC
$gccExists = Get-Command gcc -ErrorAction SilentlyContinue
$tempGccCheck = Join-Path $env:TEMP "mingw64\bin\gcc.exe"
if (!$gccExists -and !(Test-Path $tempGccCheck)) {
    Write-Host "[WARNING] GCC not found" -ForegroundColor Yellow
    $download = Read-Host "Download MinGW-w64 (provides gcc) now? (Y/n)"
    if ($download -eq 'n' -or $download -eq 'N') {
        Write-Host "[ERROR] GCC is required. Exiting." -ForegroundColor Red
        exit 1
    }

    Write-Host "[INFO] Downloading MinGW-w64..." -ForegroundColor Cyan
    $mingwUrl = "https://github.com/niXman/mingw-builds-binaries/releases/download/13.2.0-rt_v11-rev1/x86_64-13.2.0-release-posix-seh-ucrt-rt_v11-rev1.tar.xz"
    $mingwArchive = Join-Path $env:TEMP "mingw64.tar.xz"
    $mingwDir = Join-Path $env:TEMP "mingw64"

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $mingwUrl -OutFile $mingwArchive -UseBasicParsing
        Write-Host "[SUCCESS] Downloaded MinGW-w64" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download MinGW-w64: $_" -ForegroundColor Red
        exit 1
    }

    Write-Host "[INFO] Extracting MinGW-w64 (built-in tar)..." -ForegroundColor Cyan
    tar -xf $mingwArchive -C $env:TEMP 2>&1 | Out-Null

    $gccPath = Join-Path $mingwDir "bin\gcc.exe"
    if (Test-Path $gccPath) {
        $env:PATH = (Join-Path $mingwDir "bin") + ";$env:PATH"
        Write-Host "[SUCCESS] MinGW-w64 installed at: $mingwDir" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] gcc.exe not found after extraction at: $gccPath" -ForegroundColor Red
        exit 1
    }
}

# Set gcc executable path
$GCC = "gcc"
$gccCheck = Get-Command gcc -ErrorAction SilentlyContinue
if (!$gccCheck) {
    $tempGcc = Join-Path $env:TEMP "mingw64\bin\gcc.exe"
    if (Test-Path $tempGcc) {
        $GCC = $tempGcc
        $env:PATH = (Join-Path $env:TEMP "mingw64\bin") + ";$env:PATH"
    }
}

# Check for LaTeX (MiKTeX) - required by manim for DecimalNumber, MathTex, etc.
$latexExists = Get-Command pdflatex -ErrorAction SilentlyContinue
if (!$latexExists) {
    foreach ($miBin in @("$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64", "C:\Program Files\MiKTeX\miktex\bin\x64")) {
        if (Test-Path (Join-Path $miBin "pdflatex.exe")) {
            $env:PATH = "$miBin;$env:PATH"
            $latexExists = $true
            break
        }
    }
}
if (!$latexExists) {
    Write-Host "[WARNING] LaTeX not found" -ForegroundColor Yellow
    $download = Read-Host "Download MiKTeX (provides pdflatex) now? (Y/n)"
    if ($download -eq 'n' -or $download -eq 'N') {
        Write-Host "[ERROR] LaTeX is required for some demos. Skipping." -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] Downloading MiKTeX basic installer..." -ForegroundColor Cyan
        $miktexUrl = "https://mirrors.ctan.org/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe"
        $miktexInstaller = Join-Path $env:TEMP "miktex-basic-installer.exe"

        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $miktexUrl -OutFile $miktexInstaller -UseBasicParsing
            Write-Host "[SUCCESS] Downloaded MiKTeX installer" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] Failed to download MiKTeX: $_" -ForegroundColor Red
            exit 1
        }

        Write-Host "[INFO] Installing MiKTeX (silent mode)..." -ForegroundColor Cyan
        $installArgs = @("--unattended", "--user", "--package-set=basic")
        Start-Process -FilePath $miktexInstaller -ArgumentList $installArgs -Wait -NoNewWindow

        if (Test-Path (Join-Path $miktexBin "pdflatex.exe")) {
            $env:PATH = "$miktexBin;$env:PATH"
            Write-Host "[SUCCESS] MiKTeX installed at: $miktexBin" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] MiKTeX install may have failed - pdflatex not found at $miktexBin" -ForegroundColor Yellow
            Write-Host "[INFO] Try installing manually: https://miktex.org/download" -ForegroundColor Yellow
        }
    }
}

$CommonFlags = "-shared -m64"
if ($BuildConfig -eq "debug") {
    $OptimizationFlags = "-O0 -g -DDEBUG"
    $OutputSuffix = "_debug"
} else {
    $OptimizationFlags = "-O2 -DNDEBUG"
    $OutputSuffix = ""
}

$CompilerFlags = "$CommonFlags $OptimizationFlags"

$OutputName = "vulkan_core${OutputSuffix}.dll"
$OutputPath = Join-Path $OutputDir $OutputName

$SourceFiles = @(
    "platform.c",
    "vulkan_init.c",
    "vulkan_draw.c",
    "vulkan_texture.c",
    "draw/draw_rect.c",
    "draw/draw_circle.c",
    "draw/draw_line.c",
    "draw/draw_ellipse.c",
    "draw/draw_polygon.c",
    "draw/draw_dashed_line.c",
    "draw/draw_arc.c",
    "draw/draw_point.c",
    "draw/draw_text.c",
    "draw/draw_bezier.c"
)

Write-Host "[INFO] Compiling source files to object files..." -ForegroundColor Cyan
$ObjectFiles = @()
foreach ($src in $SourceFiles) {
    if (Test-Path $src) {
        $objName = $src -replace '[\\/]', '_' -replace '\.c$', '.o'
        $objPath = Join-Path $ObjDir $objName
        $ObjectFiles += $objPath

        Write-Host "[CMD] $GCC -c $CompilerFlags -o $objPath $src -I$env:VULKAN_SDK/Include" -ForegroundColor DarkGray
        & $GCC -c $CompilerFlags.Split(' ') -o $objPath $src -I"$env:VULKAN_SDK/Include"

        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Compilation failed for $src" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "[ERROR] Source file not found: $src" -ForegroundColor Red
        exit 1
    }
}

Write-Host "[INFO] Linking object files to DLL..." -ForegroundColor Cyan
Write-Host "[CMD] $GCC $CompilerFlags -o $OutputPath ..." -ForegroundColor DarkGray
& $GCC $CompilerFlags.Split(' ') -o $OutputPath $ObjectFiles -L"$env:VULKAN_SDK/Lib" -lvulkan-1 -luser32 -lgdi32

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Compilation successful!" -ForegroundColor Green
    Write-Host "[INFO] Output: $OutputPath" -ForegroundColor Cyan
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " Build Complete" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Compilation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}