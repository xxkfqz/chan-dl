@echo off
set /p urls="URLS: "
python ./chan-dl.py %urls%
pause