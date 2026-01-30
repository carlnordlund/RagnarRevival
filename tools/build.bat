@echo off
REM Build script for Ragnar Revival (Windows)
REM Usage: tools\build.bat [source_file.asm]

echo ==================================
echo   Ragnar Revival Build Script
echo ==================================
echo.

REM Check if sjasmplus is installed
where sjasmplus >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: sjasmplus not found!
    echo Please install sjasmplus and add it to your PATH
    echo Download from: https://github.com/z00m128/sjasmplus/releases
    exit /b 1
)

REM Create build directory if it doesn't exist
if not exist build mkdir build

REM If a specific file is provided, build it
if not "%~1"=="" (
    if not exist "%~1" (
        echo Error: File not found: %~1
        exit /b 1
    )

    echo Building: %~1
    sjasmplus "%~1" --lst

    if %ERRORLEVEL% EQU 0 (
        echo Build successful!

        REM List generated files
        if exist build (
            echo.
            echo Generated files:
            dir /b build
        )
    ) else (
        echo Build failed!
        exit /b 1
    )
) else (
    REM Build all .asm files in src\
    if not exist src (
        echo Error: src\ directory not found
        exit /b 1
    )

    set FAILED=0
    set SUCCEEDED=0

    for %%f in (src\*.asm) do (
        echo Building: %%f
        sjasmplus "%%f" --lst
        if %ERRORLEVEL% EQU 0 (
            set /a SUCCEEDED+=1
            echo Success
            echo.
        ) else (
            set /a FAILED+=1
            echo Failed
            echo.
        )
    )

    echo ==================================
    echo Build complete:
    echo   Succeeded: %SUCCEEDED%
    echo   Failed: %FAILED%
    echo ==================================

    REM List generated files
    if exist build (
        echo.
        echo Generated files in build\:
        dir /b build
    )

    exit /b %FAILED%
)
