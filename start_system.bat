@echo off
REM Golligog Search Engine - Complete System Startup (Windows)
REM Starts Docker (SearXNG + Redis) and Flask Backend
REM With health checks and error handling

setlocal enabledelayedexpansion

REM Colors (using ANSI codes)
set "RESET=[0m"
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"

echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%Starting Golligog Search Engine System%RESET%
echo %CYAN%============================================================%RESET%
echo.

REM Check if Docker is running
echo %BLUE%[INFO]%RESET% Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%RESET% Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo %GREEN%[OK]%RESET% Docker is running

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 0 (
    set COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>&1
    if errorlevel 0 (
        set COMPOSE_CMD=docker compose
    ) else (
        echo [ERROR] docker-compose is not installed
        pause
        exit /b 1
    )
)

echo.
echo %BLUE%[INFO]%RESET% Step 1/3: Starting Docker services (SearXNG + Redis)...
%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo %RED%[ERROR]%RESET% Failed to start Docker services
    pause
    exit /b 1
)
echo %GREEN%[OK]%RESET% Docker services started

echo.
echo %BLUE%[INFO]%RESET% Step 2/3: Waiting for SearXNG to be healthy...
set retries=0
set max_retries=30

:wait_searxng
if %retries% geq %max_retries% (
    echo %RED%[ERROR]%RESET% SearXNG failed to start
    echo %BLUE%[INFO]%RESET% Checking Docker logs...
    docker logs golligog-searxng | findstr /R "ERROR\|error" | more
    pause
    exit /b 1
)

curl -s http://localhost:8080 >nul 2>&1
if errorlevel 0 (
    echo %GREEN%[OK]%RESET% SearXNG is healthy
) else (
    set /a retries=!retries!+1
    echo %BLUE%[INFO]%RESET% Waiting... attempt !retries!/%max_retries%
    timeout /t 2 /nobreak >nul
    goto wait_searxng
)

echo.
echo %BLUE%[INFO]%RESET% Step 3/3: Starting Flask Backend...
echo.

REM Start Flask backend in a new window
start "Golligog Flask Backend" cmd /k "cd backend && python searxng_proxy.py"

REM Wait for Flask to start
timeout /t 5 /nobreak >nul

REM Check Flask health
echo %BLUE%[INFO]%RESET% Checking Flask Backend health...
curl -s http://localhost:5000/api/health >nul 2>&1
if errorlevel 0 (
    echo %GREEN%[OK]%RESET% Flask Backend is healthy
) else (
    echo %RED%[ERROR]%RESET% Flask Backend failed to start
    pause
    exit /b 1
)

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%^| SYSTEM STARTUP COMPLETE%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo %CYAN%Available Services:%RESET%
echo   * SearXNG:         http://localhost:8080
echo   * Flask Backend:   http://localhost:5000
echo   * Redis:           localhost:6379 (Docker)
echo.
echo %CYAN%API Endpoints:%RESET%
echo   * Search:          http://localhost:5000/api/search?q=query
echo   * Health Check:    http://localhost:5000/api/health
echo   * Engines List:    http://localhost:5000/api/engines
echo.
echo %CYAN%Next Steps:%RESET%
echo   1. Run Flutter app: flutter run -d chrome
echo   2. Test in browser: http://localhost:49686 (Flutter dev server)
echo   3. View SearXNG logs: docker logs -f golligog-searxng
echo.
echo %YELLOW%To stop all services: Close Flask Backend window and run: docker compose down%RESET%
echo.