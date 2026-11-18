"""Minimal screenshot diagnostic — figure out why HighResShot isn't writing files."""
import unreal
import os, glob

saved_dir = unreal.Paths.project_saved_dir() + 'Screenshots'
print(f'Saved screenshots base: {saved_dir}')

# Show every PNG already there
for sub in ('WindowsEditor', 'Windows'):
    d = os.path.join(saved_dir, sub)
    print(f'  {sub}/ exists={os.path.isdir(d)}')
    if os.path.isdir(d):
        for p in sorted(glob.glob(os.path.join(d, '*.png'))):
            print(f'    {os.path.basename(p)}  size={os.path.getsize(p)}')

# Try the console command three ways and report which world we have
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ew = ues.get_editor_world()
print(f'Editor world via UnrealEditorSubsystem: {ew}')

ew2 = unreal.EditorLevelLibrary.get_editor_world()
print(f'Editor world via EditorLevelLibrary:    {ew2}')

# Fire the command
print('Firing HighResShot 800x450 with UnrealEditorSubsystem world...')
unreal.SystemLibrary.execute_console_command(ew, 'HighResShot 800x450')

# Also try the AutomationLibrary path which can target the active viewport
try:
    print('Trying AutomationLibrary.take_high_res_screenshot...')
    unreal.AutomationLibrary.take_high_res_screenshot(800, 450, 'auto_shot.png')
    print('  AutomationLibrary call returned')
except Exception as e:
    print(f'  AutomationLibrary failed: {e}')
