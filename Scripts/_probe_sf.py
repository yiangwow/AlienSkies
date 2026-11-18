import unreal
print("EngineShowFlagsSetting props:", [p for p in dir(unreal.EngineShowFlagsSetting) if not p.startswith('_')][:15])
print("SceneCaptureSource members:", [m for m in dir(unreal.SceneCaptureSource) if m.startswith('SCS')])
