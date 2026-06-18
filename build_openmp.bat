@echo off
REM Build the OpenMP-enabled Dijkstra solver for Windows.
REM Requires MSVC cl.exe or MinGW g++ with sqlite3 available.
setlocal

where cl.exe >nul 2>&1
if %errorlevel% == 0 (
    echo Building with MSVC...
    cl /openmp /EHsc dijkstra_openmp.cpp sqlite3.lib /Fe:dijkstra_openmp.exe
    if %errorlevel% neq 0 (
        echo MSVC build failed. Ensure you are using a Developer Command Prompt.
        exit /b %errorlevel%
    )
    echo Build complete.
    exit /b 0
)

where g++ >nul 2>&1
if %errorlevel% == 0 (
    echo Building with MinGW g++...
    g++ -fopenmp -o dijkstra_openmp.exe dijkstra_openmp.cpp -lsqlite3
    if %errorlevel% neq 0 (
        echo g++ build failed. Ensure the sqlite3 development library is available.
        exit /b %errorlevel%
    )
    echo Build complete.
    exit /b 0
)

echo No supported C++ compiler found.
echo Install Visual Studio Build Tools or MinGW-w64 and rerun this script.
exit /b 1
