---
name: cypher-animation
user-invocable: false
description: Headless Blender character work for the Cypher rig pipeline — importing TRELLIS GLBs, rigging (UniRig, Rigify metarigs incl. the cat), shape keys and GNM mouths, Rhubarb lip-sync, animation craft and realism, mocap retargeting, animals, rendering and contact-sheet verification, on Blender 5.x (4.2 only where UniRig needs it). Use when writing or running a bpy script, rigging or animating a character, building face shapes or lip-sync, choosing motion data, or judging whether a render looks real.
---

# cypher-animation — rig, animate and verify characters in headless Blender

PURPOSE: one place for how we make characters move in Blender without a screen: the API facts for the build we
run, the craft rules that make motion read as real (or stylised on purpose), and the checks that prove it.
CONVENTIONS: SKILL.md is the route map and the hard rules; every detail is in `references/` beside this file.
Blender **5.2 LTS** is the default. **4.2 LTS** is used only for UniRig, whose environment pins `bpy==4.2`.
AGENT NOTES: Infra facts (which guest holds the rig workspace, its paths, the GPU queue) come from the run's
status doc or the gateway at run time, never from this file. `$R` below means the rig workspace root.
Material adapted from MIT-licensed sources is attributed in `references/sources.md`. These snippets were run on
Blender 5.2.3 on 2026-11-01: slotted action + `fcurves_for`, shape-key add/write, Rigify cat generate, weight
count, voxel remesh, `BakeOptions`, the GPU device pick, the compositor group. Re-run them after an upgrade.

## When to use

Load this skill before you write or run any `bpy` script, rig or weight a mesh, add shape keys or a mouth,
drive lip-sync, key or bake animation, retarget motion capture, rig or animate an animal, or render and
review character footage. For a GPU job also follow the queue rules in **cypher-ops**; for anything that
needs a credential use **cypher-secrets**.

## The five hard rules

1. **Inspect the API, don't guess.** Most training data is Blender 2.8–4.x and is wrong for 5.x. Before using
   an attribute, socket or enum you have not used on this build, introspect it (`references/execution.md` §4; re-probe after upgrades, `references/api-4x-5x.md` §3).
2. **Real reference, never guessed geometry.** Teeth, jaws, mouths, gaits and expressions come from a real
   model, scan, dataset or footage (GNM head, a skull scan, Muybridge, mocap). If you are about to tune a
   made-up shape for a second time, stop and find the real asset. Two attempts at one symptom, then diagnose.
3. **The metarig (or the source rig) is the truth; the generated rig is disposable.** Fix placement, roll
   and parameters in the metarig and regenerate. Never hand-edit a generated rig you will regenerate.
4. **Nothing is done until you have looked at a render of it.** Exit code 0 means nothing: `blender -b`
   returns 0 even when the script raised, and numbers have passed while the render showed broken arms.
   Every stage ends with a contact sheet you have opened (`references/render-and-verify.md`).
5. **Respect licences.** Use only motion, models and code whose licence you have read. Many video-to-motion
   tools chain to the non-commercial SMPL body model (`references/mocap-and-retargeting.md` §2).

## Execution model (detail: `references/execution.md`)

```
blender -b [file.blend] --factory-startup --python-exit-code 1 -P script.py -- <args>
```

- `-b` first; arguments run left to right, so the `.blend` comes before `-P`. Script args follow `--` and are
  read from `sys.argv[sys.argv.index("--") + 1:]`.
- One job per process. Print one machine-readable result line (`RESULT {...}` JSON) and judge the run by its
  outputs, not the exit code. Write outputs to a scratch dir, never next to the inputs.
- Prefer the data API (`bpy.data`, `bmesh`, numpy `foreach_get/foreach_set`) over operators. When an operator
  is unavoidable, use `with bpy.context.temp_override(...)` and check it returned `{'FINISHED'}`.
- Not available headless: `render.opengl` (use a Workbench render), viewport operators, brush strokes, modal
  operators, `anim.keyframe_insert` (use `datablock.keyframe_insert`). `paint.mask_flood_fill` and
  `sculpt.mesh_filter` crash. EEVEE needs a GPU context; on a box with no display use Cycles or Workbench.
- Heavy GPU renders go through the GPU queue; CPU Cycles smoke tests do not.

## 4.2 vs 5.x — the facts that bite (detail: `references/api-4x-5x.md`)

| Area | 4.2 | 5.2 |
|---|---|---|
| New shape key value | 0.0 | **1.0** — set `kb.value = 0.0` after every `shape_key_add` |
| Animation data | legacy `action.fcurves` (slots arrived in 4.4) | `action.fcurves` gone; use the slot's channelbag |
| Mix Shader / ColorRamp factor input | `Fac` | `Factor` |
| Compositor | `scene.node_tree` | `scene.compositing_node_group` + `NodeGroupOutput` |
| EEVEE engine id | `BLENDER_EEVEE_NEXT` | `BLENDER_EEVEE` |
| File Output node | `base_path`, `file_slots` | `directory`, `file_name`, `file_output_items` |
| `material.use_nodes` / `world.use_nodes` | normal | deprecated (removed in 6.0); new ones already have nodes |
| `bgl` | deprecated | removed; use `gpu` (`gpu.init()` in background) |

Same on both: Principled BSDF v2 names (`Emission Color`, `Subsurface Weight`, `Specular IOR Level`, ...);
`mesh.use_auto_smooth` absent (use Smooth by Angle); Rigify ships but is off on factory startup.

## Context rules (detail: `references/execution.md` §3)

Check the mode first; set **both** active and selected; re-set them between operator calls; update the
dependency graph before reading evaluated data; flush `bmesh` edits back (`bmesh.update_edit_mesh` in Edit
Mode, `bm.to_mesh` + `me.update()` otherwise); write the rotation property that matches `rotation_mode`;
keep the reference returned at creation (names auto-suffix `.001`).

## Importing TRELLIS GLBs (detail: `references/rigging.md` §1)

TRELLIS gives one closed skin with one texture. After `import_scene.gltf` the model is Z-up and **faces -Y**.
Expect: vertices split at UV seams (weld for any smoothing, write back through the weld map), creases that
fold inside-out (find them in plain-white renders, patch them), and too few face texels (paint the face from
the source portrait on a second UV set). Apply scale/rotation before rigging. Save `.blend`, not `.glb`,
between stages: vertex groups that are not bone names do not survive a glTF export.

## Rigging (detail: `references/rigging.md`)

- **UniRig** (4.2 env) for an automatic skeleton + skin on AI meshes; check the bone roles it found.
- **Rigify**: enable the add-on, add a metarig (`human`, `basic_human`, `basic_quadruped`, `cat`, `wolf`, `horse`),
  fit it, place joints by hand at the pivot inside the volume with knee/elbow pre-bend, generate with the
  metarig selected **and** active.
- **Auto weights fail silently.** After binding, count unweighted vertices and empty deform groups. If any,
  bind a voxel-remeshed proxy and transfer weights; strip cross-side weights; clean, limit, normalise.
- Then stress-pose and look at the joints.

## Shape keys, face and GNM mouths (detail: `references/face-and-lipsync.md`)

ARKit 52 for capture-driven faces, the 15 Oculus visemes for engine lip-sync, Rhubarb's A–H/X for our
pipeline. Our human mouth is the GNM head (Google, Apache 2.0): `c3_face.py` → `c4_gnmfit.py` → `c4_mouth.py`
swap in real lips, teeth, tongue and mouth sock as shape keys `gnm_<name>`; `c2_anim.py` drives them.
Keys are deltas from Basis, 0–1, no head motion inside a face key; correctives are driven by the keys they fix.

## Lip-sync (detail: `references/face-and-lipsync.md` §4)

Rhubarb (`-f json --extendedShapes GHX`, with the dialogue text when you have it) gives timed shapes. Never
snap to each shape: shapes blend into their neighbours, lead the sound by ~3 frames at 24 fps, M/B/P close
fully for at least 2 frames before the sound, the jaw opens big only on accents.

## Animation craft and realism (detail: `references/craft-and-realism.md`)

Block in stepped poses, spline late, never convert the whole blocking at once. Timing and spacing, ease, arcs,
anticipation, overlap, secondary motion and moving holds, with numbers. For a realistic human: breathing
12–18/min, blinks ~17/min at rest and ~26/min talking (close fast, open slower), saccades with the eyes leading
the head by ~1 frame, gaze away at phrase start and back at phrase end, small weight shifts.

## Motion capture and retargeting (detail: `references/mocap-and-retargeting.md`)

BVH/FBX import, constraint-free rest-relative retarget, bake to one slotted action per clip, clean with decimate
and smoothing, loop-check. Licence first: CMU is free incl. commercial (no resale of the data); Mixamo is
royalty-free in projects (no raw-file redistribution); AMASS, Bandai Namco and SMPL-based tools are
non-commercial.

## Animals (detail: `references/animals.md`)

Rigify `cat` metarig for the cats. Cats walk in a lateral sequence (LH→LF→RH→RF), stalk low with even
footfalls, trot from ~1 m/s, and gallop rotary only. Take timing from footage (Muybridge plates are public domain).

## Rendering and encoding (detail: `references/render-and-verify.md`)

Render image sequences, then encode with ffmpeg (`libx264 -pix_fmt yuv420p`). Set `media_type` before
`file_format` (5.x). Cycles: pick OPTIX → CUDA, OptiX denoiser on OptiX. Workbench for playblasts.

## Verify (detail: `references/render-and-verify.md` §3)

Every stage: a contact sheet (front/side/¾ + extremes + close-ups) that you open and look at, plus the numeric
gates (unweighted = 0, loop pop < 0.5°, foot slip < 1 mm, hold drift ~0, all face keys at rest = 0).
Compare against the previous good run side by side when a build or script changes.

## Gotchas

| Symptom | Cause | Fix |
|---|---|---|
| Face shows every expression at once on 5.x | new shape keys default to 1.0 | `kb.value = 0.0` after `shape_key_add` |
| `AttributeError: action.fcurves` | slotted actions (5.0) | `anim_utils.action_get_channelbag_for_slot(act, slot)` |
| Assigned action does nothing | no matching slot | set `ad.action_slot` (create one with `act.slots.new`) |
| `KeyError: 'Fac'` | socket renamed to `Factor` | index the socket or `.get("Factor") or .get("Fac")` |
| `scene.node_tree` missing | compositor node group (5.0) | `scene.compositing_node_group` |
| Bone heat failed, parent still FINISHED | non-manifold/intersecting mesh | count unweighted verts; voxel-proxy fallback |
| `rigify_generate` errors on a fitted rig | metarig not selected+active, or disjoint chain | select only it; fix joints in the metarig |
| Blender exits 0 but output missing | `-b` swallows script errors | `--python-exit-code 1`; judge by outputs |
| Render shows the dark inside of the head | TRELLIS fold-through crease | find in plain-white renders, patch |
| Hair or cloth swims through the mouth | weights or springs crossing the mouth patch | fade them out near the patch |
| Euler flip mid-turn | > 180° interpolation | quaternions, or unwrap/fix flips |
| Loop pops | first ≠ last pose; CYCLES modifier not exported | key identical ends; bake |
| Gateway refuses the command | a variable or substitution is the command word | spell the full path |
| First fetch after an edit fails its sha256 | stale transfer | fetch again; never chain `&&` after a fetch |

## Sources and licences

See `references/sources.md`: licence, copyright line and commit of every source; which text is adapted
(MIT, attributed) and which only informed the ideas (GPL, rewritten); and every cited paper and manual page.
