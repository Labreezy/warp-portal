@echo off
pip install -r requirements.txt
pyinstaller --onedir -n WarpHole -y positiondisplay.py
copy /Y script.js dist\WarpHol\

