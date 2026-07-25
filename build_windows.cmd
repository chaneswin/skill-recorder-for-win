@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py"

if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo Python not found. Install Python 3.11 or newer first.
    pause
    exit /b 1
)

%PYTHON_CMD% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)

%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name SkillRecorder recorder.py
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo.
echo Build complete: dist\SkillRecorder.exe
pause
