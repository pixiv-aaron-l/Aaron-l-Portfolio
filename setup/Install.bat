@echo off
cd /d "%~dp0"
title install

rem installs what the admin needs (python, git, a few python packages)
rem and puts a "website upload" shortcut on the desktop.
rem if python or git had to be installed, run this file one more time after.

set PY=
py -3 --version >nul 2>nul && set PY=py -3
if not defined PY (
    python --version >nul 2>nul && set PY=python
)

if not defined PY (
    echo python is missing, installing it...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    echo.
    echo close this window and run Install.bat again
    pause
    exit /b
)

git --version >nul 2>nul
if errorlevel 1 (
    echo git is missing, installing it...
    winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements
    echo.
    echo close this window and run Install.bat again
    pause
    exit /b
)

git lfs install

echo.
echo installing the python packages...
%PY% -m pip install PySide6 Pillow py7zr
if errorlevel 1 (
    echo.
    echo something went wrong with the packages, check your internet and run this again
    pause
    exit /b
)

rem pythonw is python without the black window
for /f "delims=" %%i in ('%PY% -c "import sys,os;print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"') do set PYW=%%i
for %%i in ("%~dp0..\admin") do set ADMIN=%%~fi

powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\website upload.lnk'); $s.TargetPath='%PYW%'; $s.Arguments='\"%ADMIN%\main.pyw\"'; $s.WorkingDirectory='%ADMIN%'; $s.Save()"

echo.
echo done, "website upload" is on your desktop
echo to publish you still need to link git to your github, the readme explains it
pause
