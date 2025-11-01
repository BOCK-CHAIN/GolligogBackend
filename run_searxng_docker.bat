@echo off
REM SearXNG Docker Run Script for Golligog (Windows)

echo Starting SearXNG with Docker for Golligog...
echo ==========================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 0 (
    set COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>&1
    if errorlevel 0 (
        set COMPOSE_CMD=docker compose
    ) else (
        echo Error: docker-compose is not installed.
        pause
        exit /b 1
    )
)

echo Using %COMPOSE_CMD%

REM Start SearXNG
echo Starting SearXNG and Redis services...
%COMPOSE_CMD% up -d

REM Wait for services to be healthy
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if SearXNG is running
curl -f http://localhost:8080/healthz >nul 2>&1
if errorlevel 0 (
    echo ✅ SearXNG is running successfully!
    echo 🌐 SearXNG URL: http://localhost:8080
    echo 🔍 Search API: http://localhost:8080/search
    echo.
    echo To view logs: %COMPOSE_CMD% logs -f searxng
    echo To stop: %COMPOSE_CMD% down
) else (
    echo ❌ SearXNG failed to start. Checking logs...
    %COMPOSE_CMD% logs searxng
)

pause