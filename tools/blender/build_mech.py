"""Generate the FP mech viewmodel parts. Blender space: metres, Z-up, +Y forward (away from
camera), +X right, +Z up. Exports out/mech.glb with objects Mech_LeftClaw, Mech_RightWeapon,
Mech_Struts (each carries an 'Accent' vertex-color mask: 0 on body, 1 on glow strips) and an
empty 'Muzzle' at the drill tip (firing-origin reference). Run headless:
  "<blender.exe>" --background --python tools/blender/build_mech.py
"""
import bpy, os, sys
sys.path.append(os.path.dirname(__file__))
import importlib
import lib_mech as L
importlib.reload(L)

L.clear_scene()

# ---------- RIGHT ARM: AC cannon housing + Gurren drill-tip (always-held weapon) ----------
rf = L.beveled_box('rf', (0.30, 0.55, 0.26), (0.45, 0.55, -0.30))
rh = L.beveled_box('rh', (0.34, 0.40, 0.30), (0.45, 0.95, -0.26))
rb = L.cylinder('rb', 0.12, 0.70, (0.45, 1.45, -0.24), rot=(1.5708, 0, 0))   # barrel along +Y
rd = L.cone('rd', 0.16, 0.0, 0.55, (0.45, 1.95, -0.24), rot=(1.5708, 0, 0))  # drill tip
right_body = L.join([rf, rh, rb, rd], 'rbody')
accent_r = L.beveled_box('ra', (0.36, 0.06, 0.06), (0.45, 0.80, -0.10), bevel=0.01)
L.set_accent_vertexcolor(right_body, 0.0)
L.set_accent_vertexcolor(accent_r, 1.0)
right = L.join([right_body, accent_r], 'Mech_RightWeapon')
L.add_socket('Muzzle', (0.45, 2.25, -0.24), right)

# ---------- LEFT ARM: bare heavy manipulator claw (reserved for grapple/pickup) ----------
lf = L.beveled_box('lf', (0.30, 0.55, 0.26), (-0.45, 0.55, -0.30))
lp = L.beveled_box('lp', (0.26, 0.22, 0.24), (-0.45, 0.92, -0.28))
lca = L.beveled_box('lca', (0.06, 0.30, 0.08), (-0.36, 1.10, -0.24))
lcb = L.beveled_box('lcb', (0.06, 0.30, 0.08), (-0.54, 1.10, -0.24))
left_body = L.join([lf, lp, lca, lcb], 'lbody')
accent_l = L.beveled_box('la', (0.32, 0.06, 0.06), (-0.45, 0.80, -0.10), bevel=0.01)
L.set_accent_vertexcolor(left_body, 0.0)
L.set_accent_vertexcolor(accent_l, 1.0)
left = L.join([left_body, accent_l], 'Mech_LeftClaw')

# ---------- LIGHT COCKPIT STRUTS: thin angular frame at screen edges, open center ----------
sL = L.beveled_box('sL', (0.05, 0.10, 1.30), (-0.95, 0.20, 0.0), bevel=0.01)
sR = L.beveled_box('sR', (0.05, 0.10, 1.30), (0.95, 0.20, 0.0), bevel=0.01)
sT = L.beveled_box('sT', (1.95, 0.10, 0.05), (0.0, 0.20, 0.62), bevel=0.01)
sD = L.beveled_box('sD', (1.20, 0.10, 0.10), (0.0, 0.30, -0.55), bevel=0.01)
struts = L.join([sL, sR, sT, sD], 'Mech_Struts')
L.set_accent_vertexcolor(struts, 0.0)

out_dir = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, 'mech.glb')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=out, export_format='GLB', export_yup=True,   # standard glTF: keeps up=up into UE
    export_vertex_color='ACTIVE', export_all_vertex_colors=True,
    export_active_vertex_color_when_no_material=True, export_extras=True)
print('MECH_EXPORT_OK', out, os.path.exists(out))
