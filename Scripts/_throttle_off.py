import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(w, 'Slate.bAllowThrottling 0')
unreal.SystemLibrary.execute_console_command(w, 't.MaxFPS 0')
print('throttling off, maxfps unlimited')
