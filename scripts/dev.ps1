# ReviewAI Windows PowerShell Development Helper Script

param (
    [string]$Command = "help"
)

switch ($Command.ToLower()) {
    "check" {
        Write-Host "Running Module 1 foundation verification..." -ForegroundColor Cyan
        python scripts/check_foundation.py
    }
    "test" {
        Write-Host "Running test suite..." -ForegroundColor Cyan
        pytest backend/tests
    }
    "lint" {
        Write-Host "Running linter checks..." -ForegroundColor Cyan
        ruff check backend/
        mypy backend/app
    }
    "server" {
        Write-Host "Starting backend development server..." -ForegroundColor Cyan
        uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
    }
    default {
        Write-Host "ReviewAI Dev Commands:" -ForegroundColor Yellow
        Write-Host "  .\scripts\dev.ps1 check   - Run foundation self-checks"
        Write-Host "  .\scripts\dev.ps1 test    - Run pytest test suite"
        Write-Host "  .\scripts\dev.ps1 lint    - Run ruff & mypy checks"
        Write-Host "  .\scripts\dev.ps1 server  - Launch local FastAPI server"
    }
}
