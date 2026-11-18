#include "SceneDirector.h"
#include "Materials/MaterialParameterCollection.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"

ASceneDirector::ASceneDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickInterval = 0.0f;
	bAllowTickBeforeBeginPlay = false;
}

void ASceneDirector::BeginPlay()
{
	Super::BeginPlay();

	// Load initial preset if available
	if (PresetLibrary.Num() > 0 && ActivePresetIndex < PresetLibrary.Num())
	{
		ApplyPreset(PresetLibrary[ActivePresetIndex]);
	}
}

void ASceneDirector::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	UpdateTimeOfDay(DeltaTime);

	if (bDriveLensing)
	{
		UpdateLensing();
	}
}

void ASceneDirector::UpdateLensing()
{
	if (!MPC_BlackHole)
	{
		return;
	}
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	APlayerController* PC = UGameplayStatics::GetPlayerController(World, 0);
	if (!PC || !PC->PlayerCameraManager)
	{
		return;
	}

	// Manual FOV-based projection (DPI/letterbox-independent — pure camera math; this is
	// what proved correct for the editor-viewport baking). Avoids the
	// ProjectWorldLocationToScreen + GetViewportSize pixel-space mismatch.
	// AlienCamera drives the view via SetActorRotation on the pawn directly
	// (ADR-002: bypasses the standard controller/camera pipeline). So we read rotation
	// from the pawn itself — PlayerCameraManager is NOT tracking it.
	APawn* Pawn = PC->GetPawn();
	if (!Pawn) return;
	const FVector CamLoc = Pawn->GetActorLocation();
	const FRotator CamRot = Pawn->GetActorRotation();
	const FVector Fwd = CamRot.Vector();
	const FVector Right = FRotationMatrix(CamRot).GetScaledAxis(EAxis::Y);
	const FVector Up = FRotationMatrix(CamRot).GetScaledAxis(EAxis::Z);
	const FVector ToHole = BlackHoleWorldLocation - CamLoc;
	const float Depth = FVector::DotProduct(ToHole, Fwd);

	// Defaults = effect off (hole behind camera).
	float UvX = 0.5f, UvY = 0.5f, EinsteinR = 0.1f, ShadowR = 0.06f, Strength = 0.f;

	int32 VX = 0, VY = 0;
	PC->GetViewportSize(VX, VY);
	if (Depth > 1.f && VX > 0 && VY > 0)
	{
		const float XCam = FVector::DotProduct(ToHole, Right);
		const float YCam = FVector::DotProduct(ToHole, Up);
		const float Aspect = (float)VX / (float)VY;
		const float FovDeg = PC->PlayerCameraManager->GetFOVAngle();   // horizontal FOV
		const float TanH = FMath::Tan(FMath::DegreesToRadians(FovDeg * 0.5f));
		const float TanV = TanH / FMath::Max(Aspect, 0.0001f);
		UvX = 0.5f + 0.5f * (XCam / Depth) / FMath::Max(TanH, 1e-4f);
		UvY = 0.5f - 0.5f * (YCam / Depth) / FMath::Max(TanV, 1e-4f);   // screen Y down
		const float Apparent = 0.5f * (BlackHoleRadius / Depth) / FMath::Max(TanV, 1e-4f);
		EinsteinR = Apparent * EinsteinMult;
		ShadowR = Apparent * ShadowMult;
		// Only enable effect when hole is visible on screen (with small margin so it
		// doesn't pop off abruptly at exact edge).
		const float Margin = 0.15f;
		Strength = (UvX > -Margin && UvX < 1.f + Margin && UvY > -Margin && UvY < 1.f + Margin) ? 1.f : 0.f;
	}

	// Throttled debug (read from Saved/Logs/AlienSkies.log). Also logs the engine's
	// ProjectWorldLocationToScreen for comparison.
	static float LensLogTimer = 0.f;
	LensLogTimer += World->GetDeltaSeconds();
	if (LensLogTimer > 0.5f)
	{
		LensLogTimer = 0.f;
		FVector2D PxPos(0, 0);
		PC->ProjectWorldLocationToScreen(BlackHoleWorldLocation, PxPos, false);
		UE_LOG(LogTemp, Warning,
			TEXT("LENS depth=%.0f manualUV=(%.3f,%.3f) R=%.3f str=%.1f camLoc=(%.0f,%.0f,%.0f) camYaw=%.1f camPitch=%.1f"),
			Depth, UvX, UvY, EinsteinR, Strength,
			CamLoc.X, CamLoc.Y, CamLoc.Z, CamRot.Yaw, CamRot.Pitch);
	}

	UKismetMaterialLibrary::SetScalarParameterValue(World, MPC_BlackHole, FName("BH_ScreenPosition_X"), UvX);
	UKismetMaterialLibrary::SetScalarParameterValue(World, MPC_BlackHole, FName("BH_ScreenPosition_Y"), UvY);
	UKismetMaterialLibrary::SetScalarParameterValue(World, MPC_BlackHole, FName("BH_ScreenRadius"), EinsteinR);
	UKismetMaterialLibrary::SetScalarParameterValue(World, MPC_BlackHole, FName("BH_ShadowRadius"), ShadowR);
	UKismetMaterialLibrary::SetScalarParameterValue(World, MPC_BlackHole, FName("BH_LensStrength"), Strength);
}

void ASceneDirector::SwitchToPreset(int32 PresetIndex)
{
	if (PresetIndex < 0 || PresetIndex >= PresetLibrary.Num())
	{
		return;
	}

	ActivePresetIndex = PresetIndex;
	ApplyPreset(PresetLibrary[PresetIndex]);

	OnPresetSwitched.Broadcast();
}

UScenePresetDataAsset* ASceneDirector::GetActivePreset() const
{
	if (ActivePresetIndex >= 0 && ActivePresetIndex < PresetLibrary.Num())
	{
		return PresetLibrary[ActivePresetIndex];
	}
	return nullptr;
}

void ASceneDirector::UpdateBlackHoleMPC(const FVector2D& ScreenPosition, float Mass, float LensRadius, float DiskIntensity)
{
	if (!MPC_BlackHole)
	{
		return;
	}

	// Update MPC parameters
	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_ScreenPosition_X"), ScreenPosition.X);
	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_ScreenPosition_Y"), ScreenPosition.Y);
	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_Mass"), Mass);
	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_LensRadius"), LensRadius);
	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_DiskIntensity"), DiskIntensity);
}

void ASceneDirector::UpdateTimeOfDayMPC(float SunElevation, float SunAzimuth, const FLinearColor& SkyTint, const FLinearColor& TerrainTint)
{
	if (!MPC_TimeOfDay)
	{
		return;
	}

	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_TimeOfDay, FName("SunElevation"), SunElevation);
	UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_TimeOfDay, FName("SunAzimuth"), SunAzimuth);
	UKismetMaterialLibrary::SetVectorParameterValue(GetWorld(), MPC_TimeOfDay, FName("SkyTintColor"), SkyTint);
	UKismetMaterialLibrary::SetVectorParameterValue(GetWorld(), MPC_TimeOfDay, FName("TerrainTintColor"), TerrainTint);
}

void ASceneDirector::ApplyPreset(UScenePresetDataAsset* Preset)
{
	if (!Preset)
	{
		return;
	}

	// Update sky tint
	UpdateTimeOfDayMPC(Preset->Suns.Num() > 0 ? Preset->Suns[0].InitialElevation : 30.0f,
		Preset->Suns.Num() > 0 ? Preset->Suns[0].InitialAzimuth : 180.0f,
		Preset->SkyRayleighColor,
		Preset->TerrainTintColor);

	// Update black hole parameters
	UpdateBlackHoleMPC(FVector2D(0.5f, 0.5f), Preset->BlackHole.Mass, 0.1f, Preset->BlackHole.DiskIntensity);
}

void ASceneDirector::UpdateTimeOfDay(float DeltaTime)
{
	CurrentTimeOfDay += DeltaTime * TimeOfDaySpeed;
	if (CurrentTimeOfDay >= 1.0f)
	{
		CurrentTimeOfDay = 0.0f;
	}

	// Time-of-day updates would happen here
	// (sun position, sky color, sequence playback, etc.)
}

void ASceneDirector::SetBlackHoleScreenPosition(const FVector2D& ScreenPos)
{
	if (MPC_BlackHole)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_ScreenPosition_X"), ScreenPos.X);
		UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_ScreenPosition_Y"), ScreenPos.Y);
	}
}

void ASceneDirector::SetBlackHoleMass(float Mass)
{
	if (MPC_BlackHole)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_Mass"), Mass);
	}
}

void ASceneDirector::SetBlackHoleLensRadius(float Radius)
{
	if (MPC_BlackHole)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_LensRadius"), Radius);
	}
}

void ASceneDirector::SetDiskIntensity(float Intensity)
{
	if (MPC_BlackHole)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(GetWorld(), MPC_BlackHole, FName("BH_DiskIntensity"), Intensity);
	}
}
