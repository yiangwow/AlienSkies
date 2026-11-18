@echo off
REM Capture all output to a file
cd /d E:\projects\AlienSkies

echo Attempting build at: %date% %time% > BuildLog.txt
echo. >> BuildLog.txt

"C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" Development Win64 -Project="E:\projects\AlienSkies\AlienSkies.uproject" -TargetType=Editor -Progress >> BuildLog.txt 2>&1

echo. >> BuildLog.txt
echo Build finished at: %date% %time% >> BuildLog.txt

echo Done! Check BuildLog.txt in E:\projects\AlienSkies for full output.
pause
