@echo off
cd /d E:\projects\AlienSkies
call "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" AlienSkiesEditor Win64 Development -Project="E:\projects\AlienSkies\AlienSkies.uproject" -WaitMutex
echo BUILD_EXIT_CODE=%ERRORLEVEL%
