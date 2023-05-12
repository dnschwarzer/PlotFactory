@echo off

REM Set the Python executable and pip
set PYTHON=python
set PIP=pip

REM FOR /F "tokens=2*" %%A IN ('reg query "HKCU\Software\Python\PythonCore\3.10\InstallPath" /v "" 2^>nul') DO set "PythonPath=%%B"
REM IF NOT DEFINED PythonPath (
REM     echo Python 3.10 is not installed.
REM     pause >nul
REM     exit /b 1
REM ) ELSE (
REM     echo Python 3.10 is installed at: %PythonPath%
REM )

REM set PYTHON=%PythonPath%python.exe
REM set PIP=%PythonPath%Scripts/pip3.10.exe


REM Check if the "modules_installed.json" file exists
if not exist modules_installed.json (
    echo {} > modules_installed.json
)

REM Check if the necessary modules are installed by checking the JSON file
set MODULES_INSTALLED=false
%PYTHON% -c "import json; installed = json.load(open('modules_installed.json')); required_modules = set(['matplotlib', 'numpy', 'asyncio', 'PySimpleGUI', 'scipy', 'fpdf']); installed_modules = set(installed.get('modules', [])); print('true' if required_modules.issubset(installed_modules) else 'false')" > temp.txt
set /p MODULES_INSTALLED=<temp.txt
del temp.txt

REM If the necessary modules are not installed, install them using the requirements.txt file and update the JSON file
if %MODULES_INSTALLED%==false (
    echo Installing required modules...
    %PIP% install -r requirements.txt
	
	if errorlevel 1 (
        echo Failed to install required modules.
		pause > nul
        exit /b 1
    )

    REM Update the JSON file to mark the modules as installed
    %PYTHON% -c "import json; installed = json.load(open('modules_installed.json')); required_modules = ['matplotlib', 'numpy', 'asyncio', 'PySimpleGUI', 'scipy', 'fpdf']; installed['modules'] = list(set(installed.get('modules', []) + required_modules)); json.dump(installed, open('modules_installed.json', 'w'), indent=4)"
)

REM Execute the src/main.py script
%PYTHON% src/main.py
if %errorlevel% neq 0 (
    echo An error occurred. Press any key to exit...
    pause > nul
)