#!/bin/bash
[ -d "venv" ] && source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
python req.py
clear
python main.py