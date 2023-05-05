@echo off
echo Checking for Python...
python --version > NUL 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python and add it to your PATH.
    pause
    exit /B 1
)

echo Checking for pip...
pip --version > NUL 2>&1
if errorlevel 1 (
    echo pip3 not found. Please install pip3 and add it to your PATH.
    pause
    exit /B 1
)

echo Installing required modules...
for /F "tokens=*" %%A in (requirements.txt) do (
    echo Installing %%A...
    @pip install %%A > NUL 2>&1
)

echo Running src/main.py...
python src/main.py

pause