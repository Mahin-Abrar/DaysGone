@echo off
cd /d "%~dp0"
call venv\Scripts\activate
echo Starting Life Tracker on http://0.0.0.0:8000
echo Access from other devices: http://YOUR_PC_IP:8000
ipconfig | findstr /i "IPv4"
python manage.py runserver 0.0.0.0:8000
