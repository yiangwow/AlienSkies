@echo off
cd /d E:\projects\AlienSkies

echo Regenerating project files...
"C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\GenerateProjectFiles.bat" -project="E:\projects\AlienSkies\AlienSkies.uproject" -game -engine >> build_output.log 2>&1

echo Building...
"C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat" Development Win64 -Project="E:\projects\AlienSkies\AlienSkies.uproject" -TargetType=Editor -Progress >> build_output.log 2>&1

echo Build complete! Check build_output.log for details.
pause
