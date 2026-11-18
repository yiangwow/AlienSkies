# Run this from Windows PowerShell in the AlienSkies directory

cd "C:\Users\$env:USERNAME\projects\AlienSkies"
& "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\GenerateProjectFiles.bat" AlienSkies.uproject -vs2022

if (Test-Path "AlienSkies.sln") {
    Write-Host "✅ Successfully generated AlienSkies.sln"
} else {
    Write-Host "❌ Failed to generate project files"
}
