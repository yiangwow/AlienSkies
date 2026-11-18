#include "AlienCamera.h"
#include "Camera/CameraComponent.h"
#include "InputActionValue.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputActionValue.h"
#include "GameFramework/SpringArmComponent.h"
#include "Materials/MaterialParameterCollection.h"
#include "Kismet/GameplayStatics.h"
#include "SceneDirector.h"

AAlienCamera::AAlienCamera()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickInterval = 0.0f;

	// Don't rotate actor with camera
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	// Create camera component as the root so SetActorRotation drives the view
	CameraComponent = CreateDefaultSubobject<UCameraComponent>(TEXT("CameraComponent"));
	RootComponent = CameraComponent;
	CameraComponent->bUsePawnControlRotation = false;
	CameraComponent->FieldOfView = 65.0f;
	CameraComponent->bConstrainAspectRatio = false;

	// Don't use default pawn controller input
	AutoPossessPlayer = EAutoReceiveInput::Player0;
}

void AAlienCamera::BeginPlay()
{
	Super::BeginPlay();

	UE_LOG(LogTemp, Warning, TEXT("[AlienCamera] BeginPlay - Controller=%s, IMC=%s, LookAction=%s"),
		Controller ? *Controller->GetName() : TEXT("NULL"),
		DefaultMappingContext ? *DefaultMappingContext->GetName() : TEXT("NULL"),
		LookAction ? *LookAction->GetName() : TEXT("NULL"));

	// Setup Enhanced Input
	if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
			PlayerController->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
		{
			Subsystem->AddMappingContext(DefaultMappingContext, 0);
			UE_LOG(LogTemp, Warning, TEXT("[AlienCamera] Added IMC to subsystem"));
		}

		// Capture the mouse permanently for look-around
		PlayerController->bShowMouseCursor = false;
		FInputModeGameOnly InputMode;
		PlayerController->SetInputMode(InputMode);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("[AlienCamera] No PlayerController — pawn not possessed!"));
	}


	// Force off regardless of what the level instance has serialized
	CameraComponent->bConstrainAspectRatio = false;

	// Initialize to neutral position
	TargetYaw = 180.0f;
	TargetPitch = 30.0f;
	CurrentYaw = TargetYaw;
	CurrentPitch = TargetPitch;
}

void AAlienCamera::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Drive look directly from raw mouse delta (Enhanced Input pipeline is broken in this env)
	if (APlayerController* PC = Cast<APlayerController>(Controller))
	{
		float RawMouseX = 0.f, RawMouseY = 0.f;
		PC->GetInputMouseDelta(RawMouseX, RawMouseY);
		// 3x the sensitivity for a more responsive feel
		TargetYaw += RawMouseX * MouseSensitivityScale * 3.0f;
		TargetPitch += RawMouseY * MouseSensitivityScale * 3.0f;

		// Zoom: raw mouse wheel delta (negative scroll = zoom in / lower FOV)
		float WheelDelta = PC->GetInputAnalogKeyState(EKeys::MouseWheelAxis);
		if (FMath::Abs(WheelDelta) > KINDA_SMALL_NUMBER)
		{
			TargetFOV -= WheelDelta * 5.0f;
			TargetFOV = FMath::Clamp(TargetFOV, MinFOV, MaxFOV);
		}
	}

	// Snappier interpolation (was 4.0/3.5 — too laggy for free-look)
	CurrentYaw = FMath::FInterpTo(CurrentYaw, TargetYaw, DeltaTime, 18.0f);
	CurrentPitch = FMath::FInterpTo(CurrentPitch, TargetPitch, DeltaTime, 18.0f);
	CurrentFOV = FMath::FInterpTo(CurrentFOV, TargetFOV, DeltaTime, FOVLagSpeed);

	// Don't clamp pitch in space — full 360 look is fine, you're not on a planet
	// CurrentPitch = FMath::Clamp(CurrentPitch, MinPitch, MaxPitch);

	// Apply rotation BEFORE movement so velocity uses the final orientation
	SetActorRotation(FRotator(CurrentPitch, CurrentYaw, 0.0f));
	CameraComponent->SetFieldOfView(CurrentFOV);

	// --- Movement (space-flight) ---
	if (APlayerController* PC = Cast<APlayerController>(Controller))
	{
		FVector Input = FVector::ZeroVector;
		if (PC->IsInputKeyDown(EKeys::W))           Input.X += 1.f;
		if (PC->IsInputKeyDown(EKeys::S))           Input.X -= 1.f;
		if (PC->IsInputKeyDown(EKeys::D))           Input.Y += 1.f;
		if (PC->IsInputKeyDown(EKeys::A))           Input.Y -= 1.f;
		if (PC->IsInputKeyDown(EKeys::SpaceBar))    Input.Z += 1.f;
		if (PC->IsInputKeyDown(EKeys::LeftControl)) Input.Z -= 1.f;

		if (!Input.IsNearlyZero())
		{
			Input.Normalize();
			FRotator MoveRot = bFullSixDOF
				? GetActorRotation()
				: FRotator(0.f, GetActorRotation().Yaw, 0.f);

			FVector WorldInput = MoveRot.RotateVector(FVector(Input.X, Input.Y, 0.f));
			WorldInput.Z += Input.Z;  // vertical thrust always in world Z

			float Accel = ThrustAcceleration;
			if (PC->IsInputKeyDown(EKeys::LeftShift)) Accel *= BoostMultiplier;

			Velocity += WorldInput * Accel * DeltaTime;
		}

		// Synthetic drag for control (we're in space — no air, but we still want stoppability)
		Velocity *= FMath::Max(0.f, 1.f - Drag * DeltaTime);
	}

	// Apply position delta (no collision sweep — we're in space)
	AddActorWorldOffset(Velocity * DeltaTime, false);

	// Update MPC with camera FOV
	UpdateMaterialParameterCollection();
}

void AAlienCamera::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UE_LOG(LogTemp, Warning, TEXT("[AlienCamera] SetupPlayerInputComponent - InputComp=%s, LookAction=%s"),
		PlayerInputComponent ? *PlayerInputComponent->GetClass()->GetName() : TEXT("NULL"),
		LookAction ? *LookAction->GetName() : TEXT("NULL"));

	if (UEnhancedInputComponent* EnhancedInputComponent =
		Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		EnhancedInputComponent->BindAction(
			LookAction, ETriggerEvent::Triggered, this, &AAlienCamera::HandleLookInput);
		EnhancedInputComponent->BindAction(
			ZoomAction, ETriggerEvent::Triggered, this, &AAlienCamera::HandleZoomInput);

		UE_LOG(LogTemp, Warning, TEXT("[AlienCamera] Bound IA_Look and IA_Zoom to EnhancedInputComponent"));
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("[AlienCamera] InputComponent is NOT EnhancedInputComponent! Class=%s"),
			PlayerInputComponent ? *PlayerInputComponent->GetClass()->GetName() : TEXT("NULL"));
	}
}

void AAlienCamera::HandleLookInput(const FInputActionValue& Value)
{
	UE_LOG(LogTemp, Warning, TEXT("[AlienCamera] HandleLookInput mag=%f"), Value.GetMagnitude());
	if (Value.GetMagnitude() == 0.0f) return;

	const FVector2D LookAxisValue = Value.Get<FVector2D>();

	// Yaw (left-right)
	TargetYaw += LookAxisValue.X * MouseSensitivityScale;

	// Pitch (up-down) — invert Y for typical game feel
	TargetPitch -= LookAxisValue.Y * MouseSensitivityScale;
}

void AAlienCamera::HandleZoomInput(const FInputActionValue& Value)
{
	UE_LOG(LogTemp, Warning, TEXT("[AlienCamera] HandleZoomInput mag=%f"), Value.GetMagnitude());
	if (Value.GetMagnitude() == 0.0f) return;

	const float ZoomValue = Value.Get<float>();

	// Zoom in/out (higher zoom = lower FOV)
	TargetFOV -= ZoomValue * 5.0f;
	TargetFOV = FMath::Clamp(TargetFOV, MinFOV, MaxFOV);
}

void AAlienCamera::UpdateMaterialParameterCollection()
{
	if (!SceneDirector)
	{
		return;
	}

	// Update MPC_TimeOfDay with camera FOV
	UMaterialParameterCollection* MPC = SceneDirector->GetTimeOfDayMPC();
	if (MPC)
	{
		// This is a placeholder; the actual parameter name depends on your MPC setup
		// UKismetMaterialLibrary::SetScalarParameterValue would go here when needed
	}
}
