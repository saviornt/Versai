@echo off
title Versai Training Core - Live Neural Ambience
echo ================================================
echo Versai Training Core Launcher
echo Python 3.14 + PyTorch 2.11 + RTX 3080 Ready
echo ================================================

cd /d "%~dp0"

call .venv\Scripts\activate.bat

echo Starting training core (Self-Supervised Fluency for MVP)...
python -m Versai.training

pause