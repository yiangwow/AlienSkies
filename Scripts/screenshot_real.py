"""TRUE viewport capture — exactly what the user sees, full editor post-processing
(exposure, bloom, tonemapper). Slower (~30s) than screenshot.py; use for accuracy
checks, not rapid iteration.

Writes to E:/projects/AlienSkies/Screenshots/iter.png (same path Claude reads).
"""
import unreal, os

ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
w = ues.get_editor_world()
unreal.SystemLibrary.execute_console_command(w, 'Slate.bAllowThrottling 0')

# AutomationLibrary captures the active editor viewport with full post-processing.
unreal.AutomationLibrary.take_high_res_screenshot(1280, 720, 'real_shot.png')
print('Requested true viewport capture -> Saved/Screenshots/WindowsEditor/real_shot.png')
