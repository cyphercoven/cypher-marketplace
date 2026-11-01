# Blender 4.2 vs 5.x: API facts

PURPOSE: the API differences that break or silently change our scripts, and how to write code that works on the
build we run (5.2 LTS) — plus the 4.2 forms still needed inside the UniRig environment.
CONVENTIONS: "probed" = checked on our 4.2.23 and 5.2.3 builds with a script; "docs" = from the release notes
or the sources in `sources.md`. Re-probe after any Blender upgrade (§3).
AGENT NOTES: the table in §2 merges our probe with the 5.x traps tables of Shapedsundew9/tks and
EL4CTEO/blender-skills (both MIT).

## 1. What we measured on our pipeline (probed, 2026-11-01)

| Fact | 4.2.23 | 5.2.3 |
|---|---|---|
| `ob.shape_key_add(name=..., from_mix=False).value` | 0.0 | **1.0** |
| `ShaderNodeMixShader` / `ShaderNodeValToRGB` factor input | `Fac` | `Factor` |
| `ShaderNodeMix` (float) inputs | `Factor, A, B` | same |
| `scene.node_tree` | yes | **no** — `scene.compositing_node_group` |
| File Output node props | `base_path, format, file_slots` | `directory, file_name, format, file_output_items` |
| `image_settings.media_type` | no | yes |
| `render.engine = "BLENDER_EEVEE_NEXT"` | ok | `TypeError` (`BLENDER_EEVEE`, `BLENDER_WORKBENCH`, `CYCLES`) |
| `bpy_extras.anim_utils.action_ensure_channelbag_for_slot` | no | yes |
| Rigify metarig operators | basic_human, human, basic_quadruped, cat, wolf, horse, bird, shark | same |
| Rigify enabled on factory startup | no | no |
| Principled BSDF inputs | v2 names | v2 names + `Thin Wall`, `Diffuse Roughness` |
| Cycles devices | — | OPTIX + CUDA list the GPU |

Pipeline effect: on 5.2.3 the GNM mouth keys (`gnm_*`) were all saved at 1.0, so every frame showed all mouth
shapes stacked. Our cat face script survived only because it resets every key later. Rule: **set the value**.

## 2. Writing for 5.x

**Animation (slotted actions; slots 4.4, legacy API removed 5.0):**

```python
from bpy_extras import anim_utils
act = bpy.data.actions.new("Talk")
ad = ob.animation_data_create(); ad.action = act
slot = ad.action_slot or act.slots.new(id_type="OBJECT", name=ob.name)
ad.action_slot = slot
cb = anim_utils.action_ensure_channelbag_for_slot(act, slot)
fc = cb.fcurves.ensure("location", index=2, group_name="Object Transforms")
fc.keyframe_points.insert(1, 0.0); fc.keyframe_points.insert(24, 0.1)
```

(Adapted from EL4CTEO/blender-skills, MIT.) The simplest path still works on both builds:
`scene.frame_set(f); pb.keyframe_insert("rotation_quaternion", frame=f)` creates action, slot, layer, strip and
channelbag for you. Reading curves:

```python
def fcurves_for(ad):
    """F-curves of the slot this ID is using; works on 4.2 (legacy) and 5.x (slotted)."""
    act = ad.action
    if act is None:
        return []
    if not hasattr(ad, "action_slot"):      # 4.2: no slots, legacy Action.fcurves
        return list(act.fcurves)
    if ad.action_slot is None:              # 5.x: action assigned, no matching slot
        return []                           # (Action.fcurves no longer exists here)
    cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
    return list(cb.fcurves) if cb else []
```

(Ours; RobLe3/cc-blender-skill (MIT) has a variant that walks every slot's channelbag, which also returns other
IDs' curves on a multi-slot action.)

- Assigning `ad.action` animates nothing until a slot matches; Blender auto-picks a slot only by name. Keep one
  slot name per character across takes.
- One layer per action on 5.2 (`act.layers.new()` raises on a second); layer through the NLA.
- NLA: `tr = ad.nla_tracks.new(); st = tr.strips.new("Walk", 1, act)`; set `st.action_slot` when the action has
  several slots; blend types REPLACE/ADD/COMBINE.
- Python-created drivers start with keys (0,0),(1,1) instead of a Generator modifier (5.0); remap them.
- "Only Insert Available" is on by default in 5.2 for the UI; Python `keyframe_insert` is unaffected.
- 4.5 removed Python and Rigid Body constraints; 5.0 removed `Bone.select` (use `pose_bone.select` /
  `edit_bone.select`) and `context.space_data.action`; 5.1 removed the legacy-action converter.

**Shading and rendering:**

| Old | 5.x |
|---|---|
| `bsdf.inputs["Specular"/"Subsurface"/"Transmission"/"Clearcoat"/"Sheen"/"Emission"]` | `"Specular IOR Level"`, `"Subsurface Weight"`, `"Transmission Weight"`, `"Coat Weight"`, `"Sheen Weight"`, `"Emission Color"` (+ `"Emission Strength"`, default 0) |
| `inputs["Fac"]` on Mix Shader, ColorRamp, Noise, Wave, Gradient, HueSat | `"Factor"` |
| `ShaderNodeTexMusgrave` | removed — Noise texture with `noise_type` |
| `sky_type = "NISHITA"` | `MULTIPLE_SCATTERING` (default), `SINGLE_SCATTERING`, `PREETHAM`, `HOSEK_WILKIE` |
| `scene.use_nodes; scene.node_tree` | `scene.compositing_node_group = bpy.data.node_groups.new(n, "CompositorNodeTree")` with a `NodeGroupOutput` and an interface output socket (no Composite node) |
| `mesh.use_auto_smooth` (removed 4.1) | `bpy.ops.object.shade_smooth_by_angle(angle=...)` or the Smooth by Angle modifier; normals via `mesh.corner_normals` |
| `"BLENDER_EEVEE_NEXT"` | `"BLENDER_EEVEE"`; set engines in try/except |
| `blend_method`/`shadow_method` | `surface_render_method` (4.2) |
| `material.use_nodes = True` | deprecated; new materials/worlds already have node trees |
| `image_settings.file_format = "FFMPEG"` alone | set `image_settings.media_type` first, then `file_format` |
| `mod["Socket_2"] = v` on a Geometry Nodes modifier | `mod.properties.inputs.<identifier>.value` (5.2) |
| `bpy.ops.import_scene.obj` | `bpy.ops.wm.obj_import` (also `wm.ply_import`, `wm.stl_import`, `wm.usd_import`) |
| `import bgl`, `Image.bindcode` | `gpu`, `gpu.texture.from_image()`; call `gpu.init()` in background (5.2) |
| `export_scene.gltf(filepath=...)` | add `use_active_scene=True` or `use_selection=True` (default exports all scenes) |
| `ShaderNodeMix` `inputs["A"]` | duplicated names per data type: index (`[0]` Factor, `[2]`/`[3]` A/B float, `[6]`/`[7]` A/B RGBA) |

(Rows adapted from Shapedsundew9/tks and EL4CTEO/blender-skills, both MIT.)

**Portable socket lookup:** `n.inputs.get("Factor") or n.inputs.get("Fac")`,
`b.inputs.get("Emission Color") or b.inputs["Emission"]`. Find nodes with `next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")`.

## 3. Re-probe after an upgrade

Run a probe on both builds and diff: node sockets (`[s.name for s in n.inputs if s.enabled]` for the node types
you use), `hasattr` on an instance for every attribute your scripts touch, a fresh `shape_key_add` value, the
engine enum (via the TypeError), the metarig operators and the File Output properties. Then re-run each script
on the same input under both builds and compare the logs and the renders side by side.

## 4. UniRig and 4.2

UniRig's env pins `bpy==4.2` (Python 3.11). Use the 4.2 forms only inside that env (its scripts and our calls
into it). Hand its output to 5.x as GLB/FBX and continue there. Do not upgrade that env or the 4.2 binary.
