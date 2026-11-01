# Motion capture and retargeting

PURPOSE: use real motion instead of invented motion, legally, and get it onto our rigs cleanly.
CONVENTIONS: [n] cites `sources.md` §3. Licence wording was read on 2026-11-01; re-read before shipping anything.
Not legal advice: when a licence is unclear, don't use the data for anything that leaves the house.
AGENT NOTES: import/bake/loop recipes adapted from EL4CTEO/blender-skills (MIT).

## 1. Sources of motion, by licence

| Source | Licence (short) | Commercial use? | Notes |
|---|---|---|---|
| CMU Graphics Lab Motion Capture Database | "free for all uses"; may be included in commercially-sold products; may not resell the data, even converted [31] | yes, inside a product | BVH/ASF-AMC; please acknowledge "mocap.cs.cmu.edu … NSF EIA-0196217" |
| Mixamo (Adobe) | characters and animations royalty-free for personal, commercial and non-profit projects [32] | yes, in projects | needs an Adobe ID; raw-file redistribution and ML training are not covered by the FAQ — treat as not allowed [33] |
| Rokoko free assets | usable in any project incl. commercial [39] | yes | email sign-up; redistribution not stated |
| Bandai Namco Research Motiondataset | CC BY-NC 4.0 [34] | **no** | BVH, professional actors; good for reference only |
| AMASS | non-commercial research/education/art only; no redistribution [35] | **no** | |
| Muybridge plates (1887) | public domain [60][61] | yes | timing reference for people and animals |
| Our own video | ours | yes | through a tool whose licence allows it (§2) |

## 2. Video-to-motion on one consumer GPU

Most monocular tools output **SMPL/SMPL-X** bodies, and the SMPL model licences are non-commercial (research,
education, non-commercial art; commercial use needs a Meshcapade licence) [36][37][38]. So check the tool **and**
its body model.

| Tool | Code licence | Body model | Net |
|---|---|---|---|
| GVHMR | non-commercial | SMPL/SMPL-X | non-commercial [47] |
| WHAM | MIT | SMPL | non-commercial via SMPL [48] |
| 4D-Humans / HMR 2.0 | MIT | SMPL | non-commercial via SMPL [49] |
| SMPLer-X | S-Lab 1.0 (non-commercial) | SMPL-X | non-commercial [50] |
| FreeMoCap | AGPL-3.0 | own skeleton, multi-camera | allowed under AGPL terms [51] |
| Meta SAM 3D Body | SAM licence (royalty-free; bans military/ITAR/sanctioned uses) | MHR (Apache-2.0) | allowed; single image, so run per frame and smooth [52][53] |

Run any of them through the GPU queue, one job at a time. VRAM needs on a 16 GB card are not published; measure on a
short clip first. Faces: MediaPipe Face Landmarker outputs 52 ARKit-style blendshape scores from video [26]
(check the model licence before shipping its output).

## 3. Importing

```python
bpy.context.scene.render.fps = 30                          # our delivery rate, set BEFORE importing
bpy.ops.import_anim.bvh(filepath=p, global_scale=0.01,     # 0.01 when the BVH is in centimetres
                        rotate_mode="NATIVE", use_fps_scale=True,   # resample the clip to the scene rate
                        update_scene_fps=False, update_scene_duration=True)
bpy.ops.import_scene.fbx(filepath=p, automatic_bone_orientation=True)
```

BVH options: Scale, Rotation order, Forward/Up axes (Blender is -Y forward, Z up), Start Frame, Scale FPS, Loop [41].

## 4. Retargeting

Blender has no native retarget operator; the manual points to add-ons and importers [40]. Options:

- **Constraint-free, ours** (approach from EL4CTEO's `retarget.py`, MIT): for each target bone, apply the source bone's
  world-rotation change from its rest pose onto the target's rest orientation; scale hip translation by the
  hip-height ratio; write quaternion keys straight into a new slotted action. Map bones explicitly
  (`{target: source}`), check the unmapped list (hips, upper arm, forearm, thigh, shin, head) is empty, and map spine
  chains of different lengths proportionally.
- **Rokoko Studio Live** add-on (free; both rigs in the same pose, T-pose recommended; licence files disagree:
  MIT badge vs LGPL-3 file) [43].
- **"Retarget"** extension (GPL-3+, Blender 5.0+, presets for Mixamo/VRoid/Unreal) [45]; Expy Kit (GPL-3, older) [44].
- **Auto-Rig Pro** (paid; Remap handles quadrupeds) [46].

Before retargeting, put both rigs in the same rest pose (T or A); compare a stick-figure overlay of source and
target on 5 frames before baking.

## 5. Bake, clean, loop

```python
from bpy_extras import anim_utils
opts = anim_utils.BakeOptions(only_selected=False, do_pose=True, do_object=False, do_visual_keying=True,
                              do_constraint_clear=False, do_parents_clear=False, do_clean=True,
                              do_location=True, do_rotation=True, do_scale=True, do_bbone=False,
                              do_custom_props=False)
anim_utils.bake_action(rig, action=new_action, frames=range(f0, f1 + 1), bake_options=opts)
```

(EL4CTEO, MIT.) Then:
- One action per clip, with a fake user, named `RIG|Clip`; one muted NLA track per clip so every clip exports.
- Clean noise headless with the data API: add an F-curve modifier per curve (5.1's Gaussian Smooth, or `NOISE`/
  `SMOOTH`-style modifiers), or thin keys yourself from `fcurve.keyframe_points`. `graph.decimate` and
  `graph.butterworth_smooth` are Graph Editor operators: GUI only, not available under `blender -b` (see SKILL.md).
  Keep contacts sharp: smoothing a planted foot makes it slide.
- Fix foot slip (< 1 mm while planted) with a keyed `COPY_LOCATION` pin, influence 1 → 0 at lift-off.
- Loops: identical first and last poses (pop < 0.5° / 1 mm); no speed hitch across the seam; the CYCLES F-curve
  modifier does not export, so bake it. Root carries translation and yaw; don't animate bone scale.
- Mocap is a starting point: re-time accents, push key poses (staging, silhouette), and add the face and eyes by
  hand (`craft-and-realism.md` §3).
