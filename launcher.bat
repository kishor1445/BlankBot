@echo off
if exist venv\ (
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
)
python req.py
cls
title BlankBot
python main.py
