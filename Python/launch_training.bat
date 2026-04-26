@echo off
title Versai Training Core

cd /d "%~dp0"

call .venv\Scripts\activate.bat

:: Make the main Versai package importable from plugins
set PYTHONPATH=%CD%\Versai;%PYTHONPATH%

echo ================================================
echo Versai Training Core Launcher
echo PYTHONPATH set to include main Versai package
echo ================================================

python -m Versai.core

pause