#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "ScenePresetDataAsset.generated.h"

USTRUCT(BlueprintType)
struct FSunData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun")
	FLinearColor Color = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun")
	float Brightness = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun")
	float InitialElevation = 30.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun")
	float InitialAzimuth = 180.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sun")
	float OrbitSpeed = 1.0f;
};

USTRUCT(BlueprintType)
struct FBlackHoleData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float SchwarzschildRadius = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float Mass = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float DiskInnerRadius = 20.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float DiskOuterRadius = 100.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	FLinearColor DiskCoreColor = FLinearColor(0.0f, 0.5f, 1.0f);  // blue-white

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	FLinearColor DiskMidColor = FLinearColor(1.0f, 0.8f, 0.2f);   // orange

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	FLinearColor DiskOuterColor = FLinearColor(0.8f, 0.1f, 0.0f); // red

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float DiskIntensity = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float JetLength = 5000.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	FLinearColor JetColor = FLinearColor(0.0f, 0.8f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float JetIntensity = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	float DopplerStrength = 0.5f;
};

UCLASS(BlueprintType)
class ALIENSKIES_API UScenePresetDataAsset : public UDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Preset")
	FName PresetName = TEXT("NewPreset");

	// Sky atmosphere
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sky")
	FLinearColor SkyRayleighColor = FLinearColor(0.5f, 0.0f, 1.0f);  // purple

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sky")
	float RayleighScatteringScale = 0.04f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sky")
	float MieAnisotropy = 0.95f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sky")
	float AtmosphereHeight = 60.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sky")
	FLinearColor GroundAlbedo = FLinearColor(0.15f, 0.08f, 0.04f);  // dark reddish-brown

	// Suns
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Suns")
	TArray<FSunData> Suns;

	// Black hole
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "BlackHole")
	FBlackHoleData BlackHole;

	// Terrain
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain")
	FLinearColor TerrainTintColor = FLinearColor(0.3f, 0.2f, 0.4f);

	// Post-processing
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PostProcess")
	TSoftObjectPtr<UTexture> LUTTexture;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PostProcess")
	float BloomIntensity = 1.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "PostProcess")
	float VignetteIntensity = 0.35f;
};
