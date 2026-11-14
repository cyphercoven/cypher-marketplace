# Rendering, encoding and verification

PURPOSE: render what is needed to judge the work, encode it once, and prove each stage with sheets and numbers.
CONVENTIONS: Blender 5.2; ffmpeg is `$R/tools/ffmpeg/ffmpeg` (static build). Frames first, video last.
AGENT NOTES: render settings adapted from EL4CTEO/blender-skills (MIT); gates from scenario-labs/skills (MIT).

## 1. Render

```python
sc = bpy.context.scene
sc.render.engine = "CYCLES"                      # "BLENDER_EEVEE" needs a GPU context; "BLENDER_WORKBENCH" for playblasts
prefs = bpy.context.preferences.addons["cycles"].preferences
for kind in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind; prefs.refresh_devices()
        if any(d.type == kind for d in prefs.devices): break
    except TypeError:
        continue
for d in prefs.devices: d.use = d.type != "CPU"
sc.cycles.device = "GPU"; sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.render.image_settings.media_type = "IMAGE"    # 5.x: before file_format
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = "/scratch/run/frames/"      # writes 0001.png, 0002.png …
bpy.ops.render.render(animation=True)            # or frame_set(f) + render(write_still=True)
```

- GPU renders go through the GPU queue with a label and an estimate; check no batch job is active first. CPU
  Cycles at low samples (8–24) is fine for checks and needs no queue.
- Presets: preview 64 spp / 50 % size; final 512 spp, adaptive threshold 0.01. OptiX denoiser on OptiX, else OIDN.
- `render.use_persistent_data = True` speeds animations. Split long jobs with `-s/-e` frame ranges.
- AgX is the default view transform; keep it unless matching old footage.
- `render.opengl` refuses headless: a playblast is a Workbench render (solid, matcap or flat lighting).
- Spot frames: render only the frames you need (our animation script takes `C2_MAX=N` for the first N frames and
  `C2_FRAMES=a,b,c` for chosen ones).

## 2. Encode

```
$R/tools/ffmpeg/ffmpeg -framerate 30 -i frames/%04d.png -i line.wav -c:v libx264 -pix_fmt yuv420p \
  -crf 18 -c:a aac -shortest out.mp4
```

- Render image sequences, never straight to MP4: a crash keeps the frames and a re-encode is cheap.
- Higher frame rates from a lower render rate: motion interpolation (`-vf minterpolate=fps=60:mi_mode=mci`) or a
  learned interpolator; check mouths and blinks after, they smear first.
- Keep the audio sample-accurate: `-shortest`, and check the first plosive lines up (M/B/P closed on the sound).

## 3. Verify every stage

**Contact sheets** (look at them — open the image, don't read the log):

```
$R/tools/ffmpeg/ffmpeg -i frames/%04d.png -vf "select='not(mod(n\,10))',scale=480:-2,tile=6x4" -frames:v 1 sheet.jpg
$R/tools/ffmpeg/ffmpeg -i old.png -i new.png -filter_complex "[0]scale=-2:540[a];[1]scale=-2:540[b];[a][b]hstack" cmp.jpg
```

| Stage | Sheet | Numeric gates |
|---|---|---|
| Import / mesh | front, side, ¾, back in plain white | facing -Y; scale; no black fold-through patches |
| Rig | metarig placement front/side/top; stress poses with joint close-ups | unweighted verts = 0; no empty major deform group; no cross-side weights; joint volume 0.85–1.25 |
| Face | rest, each key at 1.0, talking frames, laugh, extremes, close-ups of the mouth seam | every key 0 at rest after save; no unsculpted keys; seam gap logged |
| Lip-sync | frames on each M/B/P and each accent, with the cue label | closed lips on M/B/P ≥ 2 frames; jaw peaks on accents |
| Animation | every 5th frame; arcs plotted in camera pixels | hold drift ~0; foot slip < 1 mm; no rotation flips; loop pop < 0.5° |
| Render | first, middle, last frame at final settings | no fireflies; exposure matches the previous good run |

- **After any build or script change**, run the old and new versions on the same input and put the renders side by
  side. On 2026-11-01 every run exited 0 on 5.2 while the face was visibly broken (`api-4x-5x.md` §1).
- Arcs and spacing are judged in camera space (`bpy_extras.object_utils.world_to_camera_view` × resolution);
  normalised coordinates invent sharp turns.
- Hand the sheet to the person who approves the look; a number never substitutes for their eye.
