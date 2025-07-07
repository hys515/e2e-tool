@echo off
setlocal enabledelayedexpansion

echo ========================================
echo E2E-Tool Windows 构建脚本
echo ========================================

:: 检测可用的构建工具
set "BUILD_TOOL="
set "BUILD_ARGS="

:: 检查是否有 make
where make >nul 2>&1
if %errorlevel% == 0 (
    set "BUILD_TOOL=make"
    goto :build
)

:: 检查是否有 mingw32-make
where mingw32-make >nul 2>&1
if %errorlevel% == 0 (
    set "BUILD_TOOL=mingw32-make"
    set "BUILD_ARGS=-f Makefile.windows"
    goto :build
)

:: 检查是否有 cmake
where cmake >nul 2>&1
if %errorlevel% == 0 (
    set "BUILD_TOOL=cmake"
    goto :cmake_build
)

echo [错误] 未找到可用的构建工具
echo 请安装以下工具之一：
echo   - Make (通过 MinGW 或 MSYS2)
echo   - CMake
echo   - Visual Studio Build Tools
pause
exit /b 1

:cmake_build
echo [信息] 使用 CMake 构建...
if not exist build mkdir build
cd build
cmake ..
if %errorlevel% neq 0 (
    echo [错误] CMake 配置失败
    pause
    exit /b 1
)
cmake --build .
if %errorlevel% neq 0 (
    echo [错误] CMake 构建失败
    pause
    exit /b 1
)
echo [成功] 构建完成！
echo 可执行文件位置: build\bin\e2e-tool.exe
cd ..
goto :end

:build
echo [信息] 使用 %BUILD_TOOL% 构建...
%BUILD_TOOL% %BUILD_ARGS%
if %errorlevel% neq 0 (
    echo [错误] 构建失败
    pause
    exit /b 1
)
echo [成功] 构建完成！

:end
echo.
echo 构建命令：
echo   %BUILD_TOOL% %BUILD_ARGS%
echo.
echo 测试命令：
if "%BUILD_TOOL%"=="cmake" (
    echo   cd build ^&^& ctest
) else (
    echo   %BUILD_TOOL% %BUILD_ARGS% test
)
echo.
pause 