# Importing and rigging

PURPOSE: get an AI-generated mesh (TRELLIS) to a rig that deforms cleanly, with checks that catch the silent failures.
CONVENTIONS: Blender 5.2 unless marked; UniRig runs in its own 4.2 env. Metres, Z up, character faces -Y.
AGENT NOTES: craft rules and numbers adapted from scenario-labs/skills and EL4CTEO/blender-skills (both MIT);
see `sources.md`.

## 1. TRELLIS GLB in

```python
bpy.ops.import_scene.gltf(filepath=glb)
```

- Result: Z up, the face looks along **-Y**, units metres. Check `ob.dimensions` (a person ~1.6–1.9 m) and which
  way the face points before anything else; our animation script logs it (`FACING [x, -1, 0]`).
- One closed skin, one texture atlas. The face gets few texels, so lips blur; paint the face from the source
  portrait onto a second UV set, fitted on face landmarks, with a feathered mask.
- glTF splits vertices at UV seams. Any smoothing works on welded positions and writes back through the weld map,
  or the seams crack. Don't merge-by-distance on the export copy.
- Creases fold through themselves and show the dark inside of the head as black marks. Find them in plain-white
  renders from several angles and lay a textured patch over each.
- Nothing behind the lips: a mouth needs a real interior (GNM, `face-and-lipsync.md` §3).
- Many disconnected islands (hair cards, eyes, accessories) break bone heat. Note them; they get rigid weights or
  a proxy transfer.
- Before rigging: transforms applied (`me.transform(ob.matrix_world, shape_keys=True)`, then identity), feet at
  Z=0, centred on X, facing -Y.
- Save `.blend` between stages: vertex groups that are not bone names do not survive a glTF export.

## 2. UniRig (automatic skeleton and skin)

Runs in `envs/unirig` (bpy 4.2, Python 3.11). Feed it the GLB; it returns a skeleton FBX and a skinned FBX/GLB
with generic bone names (`bone_0…`). Afterwards, in 5.x:

- identify roles (head, neck, spine chain, limbs) from bone positions, not names, and log them;
- check the weights like any auto-weights (§4) — AI skins leak across the mouth and between legs;
- for faces, keep head turns on the neck chain and let shape keys (not bones) move the mouth.

## 3. Rigify

```python
import addon_utils; addon_utils.enable("rigify", default_set=True, persistent=False)
bpy.ops.object.armature_human_metarig_add()      # or basic_human, basic_quadruped, cat, wolf, horse
meta = bpy.context.object
```

**Placement is the spec** (scenario-labs, MIT):
- Joints sit at the pivot of rotation, in the middle of the volume they move.
- Knees and elbows get a small pre-bend (1–3°; about 1.2 % of limb length off the straight line), knees forward,
  elbows back. The bend, not the roll, decides where the IK pole lands.
- Roll puts each hinge on one local axis, so the animator works one F-curve.
- Spine 3–5 bones, neck 1–2. Twist bones stop candy-wrapping.
- Write each bone end once: moving a parent's tail in Edit Mode moves a connected child's head.
- `armature.symmetrize()` needs side names it recognises; `lid.T.L.001` does not end in `.L`.

**Landmarks from the mesh** (scenario-labs): crotch = first horizontal cut whose loop spans x=0; hip 13 % of
crotch height above it; ankle = first cut that turns round; knee halfway on hip–ankle; neck = narrowest central
section, head pivot 20 % of head height above it; wrist = narrowest section at 60–90 % of the arm; elbow at 53 %.

**The metarig is the source; the generated rig is disposable.** Every fix goes into the metarig bones, Rigify
parameters or a post-generation script (`meta.data.rigify_finalize_script = bpy.data.texts["postgen.py"]`).
Regenerating keeps control names, so weights and animation survive.

**Generate:**

```python
for o in bpy.context.view_layer.objects: o.select_set(False)
meta.select_set(True); bpy.context.view_layer.objects.active = meta
bpy.ops.pose.rigify_generate()
rig = meta.data.rigify_target_rig          # object named "rig" by default; rename it per character
```

Probed on 5.2.3: the cat metarig generates (760 bones) headless with exactly these steps.

Errors name the bone ("bone position is disjoint", "Expected 2 eye corners"); most are separated joints. A failed
generate leaves a partial rig. The Human metarig carries the legacy face: run Upgrade Face after fitting and
before generating (irreversible). Generated controls: `upper_arm_fk.L`, `hand_ik.L`, `upper_arm_parent.L`
(`IK_FK`: 1 = FK), `thigh_fk.L`, `foot_ik.L`, `torso` (`neck_follow`, `head_follow`); deform bones start `DEF-`.

## 4. Skinning: auto weights fail silently

`parent_set(type="ARMATURE_AUTO")` returns FINISHED even when bone heat failed. Always measure:

```python
import numpy as np
def unweighted(ob, deform_names, eps=1e-4):
    idx = {g.index for g in ob.vertex_groups if g.name in deform_names}
    return sum(1 for v in ob.data.vertices if not any(g.group in idx and g.weight > eps for g in v.groups))
```

Also count major deform bones whose group is empty (small face, teeth, tongue bones may be empty legitimately).

**Fallback: voxel proxy + Data Transfer** (EL4CTEO, MIT; voxel schedule from scenario-labs):
1. Copy the mesh (`ob.copy()`, `data.copy()`), clear its modifiers and groups, unparent it keeping `matrix_world`.
2. `proxy.data.remesh_voxel_size = H/180` (H = character height), `voxel_remesh()`; bind the proxy with
   ARMATURE_AUTO. If heat still misses proxy vertices, retry at H/90, then H/45 (coarser closes holes).
3. On the real mesh: clear groups, add a `DATA_TRANSFER` modifier from the proxy (`use_vert_data`,
   `data_types_verts={"VGROUP_WEIGHTS"}`, `vert_mapping="POLYINTERP_NEAREST"`, `layers_vgroup_select_src="ALL"`,
   `layers_vgroup_select_dst="NAME"`), `datalayout_transfer`, move it to index 0, **apply** it, delete the proxy.
4. Strip cross-side weights (`.L` weight on the right half), assign rigid islands (eyes, teeth) at 1.0 to one bone,
   remove groups for non-deform bones.
5. `vertex_group_clean(limit=0.01)`, `vertex_group_limit_total(limit=4)` for export (8 on PC),
   `vertex_group_normalize_all(lock_active=False)`.

Weight rules: blend 50/50 at the joint line over 1–2 edge loops; limit each seam to 2–3 bones; firm beats mushy;
head is 100 % head above the jawline; garments get their weights from the body by an *applied* transfer; Armature
modifier after shape-key-like deforms and before Subdivision/Corrective Smooth. Heat fails on non-manifold or
intersecting parts and tiny scale.

## 5. Stress test and correctives

Pose the extremes (arms up 70°, forward 60° with 130° elbows, hip flexed 90° + knee 120°, crouch, spine twist 45°,
head 70°) and render front/side close-ups of every joint. Gates (scenario-labs): joint volume 0.85–1.25 of rest,
no leak > 0.001 H, edge strain within 0.5–1.6. Then open the sheet: numbers have passed with broken arms on screen.

Correctives: sculpting is not available headless, so build the target from data (restore flesh to its rest
distance, or solve the offset through the skinning) and save it as a shape key driven by the joint angle
(`ROTATION_DIFF` between two ORG bones that follow both IK and FK; keys at the start and full bend, clamped).
Fix order: placement/roll → metarig → regenerate; weights → data edits; volume → correctives.
