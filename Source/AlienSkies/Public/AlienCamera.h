#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "InputActionValue.h"
#include "SceneDirector.h"
#include "AlienCamera.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UInputMappingContext;
class UInputAction;
class UEnhancedInputComponent;

UCLASS()
class ALIENSKIES_API AAlienCamera : public APawn
{
	GENERATED_BODY()

public:
	AAlienCamera();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

protected:
	// Components
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	UCameraComponent* CameraComponent;

	// Input System
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputMappingContext* DefaultMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* LookAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* ZoomAction;

	// Camera parameters
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float CurrentYaw = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float CurrentPitch = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float TargetYaw = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float TargetPitch = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float CurrentFOV = 65.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float TargetFOV = 65.0f;

	// Camera tuning
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float YawLagSpeed = 4.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float PitchLagSpeed = 3.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float FOVLagSpeed = 3.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float MinPitch = -30.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float MaxPitch = 85.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float MinFOV = 15.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float MaxFOV = 110.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float MouseSensitivityScale = 0.15f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera|Tuning")
	float GamepadSensitivityScale = 60.0f;

	// --- Movement (space-flight feel; Straftat-fast at galactic scale) ---
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float ThrustAcceleration = 200000.f;  // cm/s^2

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float BoostMultiplier = 3.0f;  // hold shift = afterburner

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float Drag = 0.4f;  // velocity decays this fraction per second with no input

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	bool bFullSixDOF = false;  // false = WASD relative to yaw only (FPS feel); true = full 3D camera-relative

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "Movement")
	FVector Velocity = FVector::ZeroVector;

	// Input callbacks
	void HandleLookInput(const FInputActionValue& Value);
	void HandleZoomInput(const FInputActionValue& Value);

	// MPC update
	UPROPERTY()
	ASceneDirector* SceneDirector;

	void UpdateMaterialParameterCollection();

public:
	// Getters
	UFUNCTION(BlueprintCallable, Category = "Camera")
	float GetCurrentYaw() const { return CurrentYaw; }

	UFUNCTION(BlueprintCallable, Category = "Camera")
	float GetCurrentPitch() const { return CurrentPitch; }

	UFUNCTION(BlueprintCallable, Category = "Camera")
	float GetCurrentFOV() const { return CurrentFOV; }
};
