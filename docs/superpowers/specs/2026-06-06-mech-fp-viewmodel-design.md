# Mech First-Person Viewmodel — Design Spec

**Date:** 2026-06-06
**Status:** Approved (design); ready for implementation plan
**Project:** Alien Skies (UE5.7, cosmic-arena FP action)

## Context

The vision (project `CLAUDE.md` §1) already calls for a mech avatar: *"Armored Core /
Chromehounds / Gundam … the humanoid/mech avatar should feel like a piloted machine, not a
person."* No character/avatar asset exists yet — only the camera pawn (`AAlienCamera`),
`BP_SceneDirector`, and scene presets. This spec covers building that avatar as a
**first-person mech viewmodel**.

The project builds **environment first**; movement, combat, and networking come later. This
deliverable is the visible piloted mech and nothing more — but it is designed so combat and
networked multiplayer bolt on cleanly afterward.

## Decisions (locked during brainstorming)

| Decision | Choice |
|---|---|
| Perspective | First-person mech viewmodel (cockpit/arms), preserves existing FP camera/movement |
| Cockpit weight | Light — arms/weapon + thin canopy struts; vista stays open in the center |
| Geometry source | **Blender headless, code-driven** (`bpy`, `--background`) → glTF → UE import. User never opens Blender. |
| Aesthetic | Hybrid: Armored-Core angular chassis + Gurren emissive glow |
| Scope | Model + idle life (sway/bob, thruster flicker). No firing, no pickup, no grapple. |
| Weapon | One fixed always-held weapon, mounted in a **swappable slot** (forward-compat for pickup/types) |

## 1. Aesthetic & Layout

Light-cockpit FP viewmodel, hybrid AC-chassis + Gurren-glow:

- **Right arm** — the signature **integrated always-held weapon**: chunky AC-style cannon
  housing with a **Gurren drill-tip** and an emissive energy core. Carries a **muzzle socket**
  (origin for future firing).
- **Left arm** — a bare heavy **manipulator/claw**, deliberately weapon-free; reserved for
  future grappling and weapon pickup.
- **Canopy struts** — thin angular frame at the screen edges + a sliver of dashboard; never
  crowds the center so the cosmic vista stays dominant.
- **Emissive accents** — panel accent lines + thruster vents, tinted to the cosmic palette
  (cyan/orange), intensity live-tunable so they read against the scene's heavy bloom without
  blowing out.

## 2. Build Pipeline (all code; user never opens Blender)

```
tools/blender/build_mech.py        (bpy: boxes -> bevel -> boolean -> greeble detail)
        |   blender --background --python build_mech.py
        v
tools/blender/out/mech.glb         (named objects + sockets, separate parts)
        |   Scripts/import_mech.py (UE Python import bridge)
        v
Content/AlienSkies/Mech/           (static meshes + M_MechHybrid material)
```

- **Separate objects per part** (L-arm, R-arm+weapon, struts) so each places/animates
  independently and the weapon can be swapped later.
- **Static meshes, not skeletal** — idle motion is procedural component transforms (no rig),
  keeping everything code/param-driven and simple.
- The import bridge handles **Blender↔UE conversion**: metres↔centimetres, Z-up handedness,
  and socket/orientation alignment.
- Accent-glow mask authored in Blender (vertex color or a 2nd UV) and read by the material.

## 3. Integration & Idle Life (UE side)

- **`BP_MechViewmodel`** actor attaches to the FP camera (`AAlienCamera`) component at
  BeginPlay and parents the mesh parts in front of the view. *Blueprint, not C++* — avoids full
  rebuilds (ADR-006) and stays fast to tune.
- **`WeaponSlot`** scene component on the right hand holds the current weapon mesh — hard-set to
  the fixed weapon now, swappable later.
- **Idle life (procedural, cheap):** sine-based **sway/bob** + **look-velocity lag** (arms trail
  view turns slightly → sells weight) + **thruster emissive flicker**. All tunable live via
  params/MPC, consistent with the rest of the project.
- **`M_MechHybrid`** material: brushed-metal base + masked emissive accent channel (`AccentGlow`
  scalar) + thruster glow. Hooked to the MPC bus (ADR-001) for live tuning.

## 4. Forward-Compatibility (cheap hooks; features themselves are OUT of scope)

Baked in now so combat / pickup / netcode slot in without reworking the model:

1. **Muzzle socket** on the weapon mesh → firing origin for the future `WeaponComponent`.
2. **Swappable `WeaponSlot`** → serves both future weapon pickup and multiple weapon types.
3. **Cosmetic/gameplay separation** — the mech is a Pawn carrying a *cosmetic* viewmodel;
   gameplay components (Health/Weapon) attach later without touching the viewmodel. Keep them
   cleanly separable.

## 5. Future Phases (documented, NOT in this deliverable)

Roadmap so the path is visible:

1. **Mech viewmodel + idle life** ← *this spec*
2. **Combat core (solo):** `HealthComponent` (`MaxHealth`/`CurrentHealth`/`OnDeath`),
   `WeaponComponent` (hitscan or projectile, fire rate, damage, muzzle FX), damage via
   `ApplyPointDamage`/`TakeDamage`, death → explosion + respawn (GameMode), scoring.
   **This phase adds the real C++ Automation logic unit tests** (damage→health→death, fire
   rate) on the pipeline established in the mech phase (ADR-012).
   - Decision deferred to a future ADR: plain UE damage (start simple) vs Gameplay Ability
     System / GAS (heavier, replication-built-in; adopt only when abilities/cooldowns pile up).
3. **Networked test via Hamachi:** UE **listen server** — one player hosts and plays
   (`open Arena?listen`), friend joins via the host's Hamachi `25.x.x.x` IP (`open <ip>`). No
   port forwarding / online subsystem. Requires making movement, weapon-fire (Server RPC +
   Multicast FX), health, and death **replicate** — the real netcode phase.
   - Note: `AAlienCamera`'s Enhanced-Input bypass (ADR-002) and the custom movement may need
     revisiting for networked prediction.
4. **PvP arena polish:** scoring, spawns, multiple mechs.

## 6. ADRs to Record

- **ADR-010 — Amend the no-Blender rule.** Blender is permitted **strictly headless and
  script-driven** (`bpy`, `--background`), never manual. Generated meshes are reproducible from
  committed scripts. Rationale: real mesh fidelity without losing the in-house / reproducible
  ethos; the original rule existed only because manual Blender use was off the table.
- **ADR-011 (stub) — Combat & networking direction.** Records the future-phase direction above
  (UE damage→possibly GAS; Hamachi listen-server for early multiplayer test). Kept out of scope
  here; expanded into its own spec when Phase 2 begins.
- **ADR-012 — Two-layer testing.** Python asset-validation harness (`run_tests.py`) for
  data/visual content + UE C++ Automation for logic unit tests (example now, real tests with
  combat). Established now because the user is new to UE and wants sustainable foundations.

## 7. Verification (two-layer testing — ADR-012)

The mech is mostly data/visual, so testing is layered:

1. **Asset/scene validation** — `Scripts/run_tests.py`, a one-command harness that asserts the
   meshes imported, scale is sane, the muzzle socket exists, the material compiled, and the
   viewmodel is attached. Prints PASS/FAIL; run headless via the UE Python path.
2. **Logic unit tests** — UE **C++ Automation** framework (`Source/AlienSkies/Private/Tests`),
   run headless via `UnrealEditor-Cmd ... "Automation RunTests ..."`. One example test now to
   prove the pipeline; **real Health/Weapon logic tests land with the combat phase** (no
   meaningful logic to unit-test in the viewmodel itself).
3. **Visual judgment** — FP-view SceneCapture screenshots for composition/placement; the user
   confirms final glow/idle feel in **Standalone (Alt+P)** (offline SceneCapture under-blooms —
   established project limitation).

The user is new to UE; this establishes the testing pipeline early and cheaply so the project
stays maintainable as combat and networking are added.

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Blender install + headless invocation from `cmd.exe` untested | Verify a trivial `bpy` script runs headless **before** building the mech |
| glTF orientation/scale mismatch (m↔cm, handedness) | Handle in the import bridge; verify with a known-size test cube first |
| FP viewmodel near-clip clipping | Tune placement/scale now; defer a full separate-viewmodel render pass to later polish |
| Slower iteration than pure-UE | Split work: infrequent Blender geometry rebuilds vs live UE tuning of material/idle/placement |
| Emissive accents blow out under scene bloom | `AccentGlow` scalar is live-tunable; judge in Standalone |

## 9. Out of Scope (explicit)

Weapon firing/projectiles · weapon pickup/swap logic · grappling · third-person body · full
cockpit · health/damage/death · networking/replication · GAS.

## Asset & File Additions

- `tools/blender/build_mech.py` (+ helper libs as needed)
- `tools/blender/out/mech.glb` (generated; consider gitignoring the binary, committing the script)
- `Scripts/import_mech.py` (UE Python import bridge)
- `Content/AlienSkies/Mech/` (static meshes, `M_MechHybrid`, material instance)
- `Content/AlienSkies/Blueprints/BP_MechViewmodel.uasset`
- `CLAUDE.md`: ADR-010 + ADR-011 stub + diary entry + asset-map update
