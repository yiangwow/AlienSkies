# Install .NET Framework SDK via Visual Studio Installer

$installerPath = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe"
$vsPath = "C:\Program Files\Microsoft Visual Studio\2022\Professional"

if (-not (Test-Path $vsPath)) {
    Write-Host "Visual Studio 2022 Professional not found at $vsPath"
    exit 1
}

if (-not (Test-Path $installerPath)) {
    Write-Host "Visual Studio Installer not found"
    exit 1
}

Write-Host "Installing .NET Framework SDK for Visual Studio 2022 Professional..."
Write-Host "This will take several minutes..."

# Run the installer to add .NET Framework SDK components
# The --add parameters specify the workload components to add
& $installerPath modify `
    --installPath $vsPath `
    --add "Microsoft.VisualStudio.Workload.NativeDesktop" `
    --add "Microsoft.VisualStudio.Component.VC.Tools.x86.x64" `
    --norestart `
    --passive

Write-Host "Installation complete! You may need to restart your computer."
Write-Host "After restart, try building the UE5 project again."
