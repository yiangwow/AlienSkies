"""Trigger Live Coding compile from Python."""
import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(w, 'LiveCoding.Compile')
print('Live Coding compile requested')
