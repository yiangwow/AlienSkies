// Screen-space point-mass gravitational lens (shared by build_pp_lensing.py [MPC-driven,
// runtime] and set_bh_screen.py [literal-baked, editor preview]).
// Inputs: UV (screen uv), Cx,Cy (hole screen center), R (Einstein radius, screen-HEIGHT
// units), ShadowR (event-horizon dark radius), Strength (0..1 master).
float2 C = float2(Cx, Cy);
float aspect = View.ViewSizeAndInvSize.x * View.ViewSizeAndInvSize.w;  // width/height

float2 dd = UV - C;
dd.x *= aspect;                          // circular lens in screen space
float r = length(dd);
float2 dir = (r > 1e-5) ? dd / r : float2(0.0, 1.0);

// Lens equation (point mass): observed radius r maps to source radius r - R^2/r.
// Allowed to go negative so the dir flips -> the far side of the disk is pulled across
// the center and appears wrapped OVER the shadow (the iconic M87 arc).
float bend = (R * R) / max(r, 1e-4);
float rb = r - bend * Strength;

float2 sd = dir * rb;
sd.x /= aspect;
float2 uvL = C + sd;

float3 orig = SceneTextureLookup(UV, 14, false).rgb;                 // 14 = PPI0
float3 lensed = SceneTextureLookup(saturate(uvL), 14, false).rgb;

// Out-of-screen samples would smear the clamped edge (blocky band) -> fall back to the
// undistorted pixel there.
float oob = (uvL.x < 0.0 || uvL.x > 1.0 || uvL.y < 0.0 || uvL.y > 1.0) ? 0.0 : 1.0;
float3 col = lerp(orig, lensed, oob);

// Smooth far-field return to identity so the outer boundary isn't a hard circle and
// distant space stays pristine.
float NearR = R * 1.5;
float FarR  = R * 3.5;
float fall = saturate((FarR - r) / max(FarR - NearR, 1e-4));         // 1 inside, 0 far
col = lerp(orig, col, fall * saturate(Strength));

// Event-horizon shadow: dark disk at center (gated by Strength so Strength==0 is a true
// no-op pass-through).
float shadow = smoothstep(ShadowR * 0.82, ShadowR, r);
col *= lerp(1.0, shadow, saturate(Strength));

return col;
