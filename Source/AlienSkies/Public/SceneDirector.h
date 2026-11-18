#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ScenePresetDataAsset.h"
#include "SceneDirector.generated.h"

class UMaterialParameterCollection;

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPresetSwitched);

UCLASS()
class ALIENSKIES_API ASceneDirector : public AActor
{
	GENERATED_BODY()

public:
	ASceneDirector();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	// Preset system
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Presets")
	TArray<TObjectPtr<UScenePresetDataAsset>> PresetLibrary;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Presets")
	int32 ActivePresetIndex = 0;

	// Material Parameter Collections
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
	TObjectPtr<UMaterialParameterCollection> MPC_BlackHole;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Materials")
	TObjectPtr<UMaterialParameterCollection> MPC_TimeOfDay;

	// Post-process gravitational lensing — per-frame driver (projects the hole's world
	// position to screen each frame so the lens stays anchored to the black hole).
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lensing")
	bool bDriveLensing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lensing")
	FVector BlackHoleWorldLocation = FVector(-620000.f, 0.f, 230000.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lensing")
	float BlackHoleRadius = 13000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lensing")
	float EinsteinMult = 2.1f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lensing")
	float ShadowMult = 1.1f;

	// Time of day
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TimeOfDay")
	float TimeOfDaySpeed = 0.05f;  // 20x slower than real time

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "TimeOfDay")
	float CurrentTimeOfDay = 0.0f;

	// Level sequence for animation - handle in Blueprint instead

	// Events
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnPresetSwitched OnPresetSwitched;

	// Public functions
	UFUNCTION(BlueprintCallable, Category = "Presets")
	void SwitchToPreset(int32 PresetIndex);

	UFUNCTION(BlueprintCallable, Category = "Presets")
	int32 GetActivePresetIndex() const { return ActivePresetIndex; }

	UFUNCTION(BlueprintCallable, Category = "Presets")
	UScenePresetDataAsset* GetActivePreset() const;

	UFUNCTION(BlueprintCallable, Category = "Materials")
	UMaterialParameterCollection* GetBlackHoleMPC() const { return MPC_BlackHole; }

	UFUNCTION(BlueprintCallable, Category = "Materials")
	UMaterialParameterCollection* GetTimeOfDayMPC() const { return MPC_TimeOfDay; }

	// MPC updates
	UFUNCTION(BlueprintCallable, Category = "Materials")
	void UpdateBlackHoleMPC(const FVector2D& ScreenPosition, float Mass, float LensRadius, float DiskIntensity);

	UFUNCTION(BlueprintCallable, Category = "Materials")
	void UpdateTimeOfDayMPC(float SunElevation, float SunAzimuth, const FLinearColor& SkyTint, const FLinearColor& TerrainTint);

protected:
	void ApplyPreset(UScenePresetDataAsset* Preset);
	void UpdateTimeOfDay(float DeltaTime);
	void UpdateLensing();

	// Visualization
	FVector2D GetBlackHoleScreenPosition() const;

public:
	// Direct parameter setters for convenience
	void SetBlackHoleScreenPosition(const FVector2D& ScreenPos);
	void SetBlackHoleMass(float Mass);
	void SetBlackHoleLensRadius(float Radius);
	void SetDiskIntensity(float Intensity);
};
