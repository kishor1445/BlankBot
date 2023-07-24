@echo off
if exist venv\ (
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
)
pip install -r requirements.txt
cls
title BlankBot
python main.py
