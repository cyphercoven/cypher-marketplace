# Shape keys, faces, GNM mouths and lip-sync

PURPOSE: build faces that move like faces: standard shape sets, our GNM mouth pipeline, and lip-sync that blends.
CONVENTIONS: Blender 5.2. A character faces -Y, so its own left is +X (the `.L` side).
AGENT NOTES: shape-key mechanics adapted from EL4CTEO/blender-skills and scenario-labs/skills (MIT); research
numbers cited by number to `sources.md` §3.

## 1. Shape-key mechanics

- Keys are deltas from Basis. Never change Basis topology after making keys. Range 0–1. Names are exact and
  case-sensitive. Only relative keys export.
- **Set the value**: on 5.x `shape_key_add` leaves the new key at 1.0.
  ```python
  if not me.shape_keys: ob.shape_key_add(name="Basis", from_mix=False)
  kb = ob.shape_key_add(name="jawOpen", from_mix=False); kb.value = 0.0
  kb.data.foreach_set("co", new_coords.ravel())          # write the shape headless (float32 array)
  ```
- `from_mix=True` bakes the current mix: useful for combinations, dangerous by accident.
- Split a symmetric key into L/R with a soft blend across X=0 (EL4CTEO, MIT):
  `w_left = np.clip(0.5 + x / (2 * max(falloff, 1e-6)), 0, 1)` (character left = +X), then
  `basis + delta * w[:, None]`.
- Report empty keys: max offset `np.linalg.norm(co - basis, axis=1).max() < 1e-6` means unsculpted. Empty keys and
  their names survive FBX/GLB, so an export can list all 52 names and animate nothing.
- Applying modifiers on a mesh with keys fails; use `modifier_apply_as_shapekey`. Subdivision goes after the keys.
- Correctives for combinations (`jawOpen_mouthSmile`): a SCRIPTED driver `a*b` on the key, two `SINGLE_PROP`
  variables reading `key_blocks["jawOpen"].value` and `key_blocks["mouthSmile"].value`. Simple expressions run
  without Python auto-exec. Drivers on keys live on the Key ID (`me.shape_keys`).
- No head or neck motion inside a face key; the neck bones do that.

## 2. Standard shape sets

**ARKit 52** (Apple `ARFaceAnchor.BlendShapeLocation`, values 0–1) [22]: eyes 14 (`eyeBlink`, `eyeLookDown`,
`eyeLookIn`, `eyeLookOut`, `eyeLookUp`, `eyeSquint`, `eyeWide`, each Left/Right); jaw 4 (`jawForward`, `jawLeft`,
`jawRight`, `jawOpen`); mouth 23 (`mouthClose`, `mouthFunnel`, `mouthPucker`, `mouthLeft`, `mouthRight`, Left/Right
`mouthSmile`, `mouthFrown`, `mouthDimple`, `mouthStretch`, `mouthPress`, `mouthLowerDown`, `mouthUpperUp`, plus
`mouthRollLower`, `mouthRollUpper`, `mouthShrugLower`, `mouthShrugUpper`); brows 5 (`browDownLeft/Right`,
`browInnerUp`, `browOuterUpLeft/Right`); cheeks 3 (`cheekPuff`, `cheekSquintLeft/Right`); nose 2
(`noseSneerLeft/Right`); `tongueOut`. Left/Right are the face's own sides, so Left keys move +X. `mouthClose` is lip
closure independent of the jaw: pair it with `jawOpen` to seal the lips on an open jaw.

**FACS mapping** (community cheat sheet, not Apple [24]): browInnerUp AU1, browOuterUp AU2, browDown AU4, eyeWide
AU5, cheekSquint AU6, eyeSquint AU7, eyeBlink AU45, noseSneer AU9, mouthUpperUp AU10, mouthSmile AU12, mouthDimple
AU14, mouthFrown AU15, mouthLowerDown AU16, mouthShrug AU17, mouthPucker AU18, mouthStretch AU20, mouthFunnel AU22,
mouthPress AU24, mouthRoll AU28, jawOpen AU26/27, cheekPuff AD34. ARKit has nothing for AU11, AU13, AU23.
FACS itself: Ekman & Friesen, 1978, revised 2002 [21].

**15 visemes** (Meta/Oculus Lipsync): `sil`, `PP` (p b m), `FF` (f v), `TH`, `DD` (t d), `kk` (k g), `CH` (ch j sh),
`SS` (s z), `nn` (n l), `RR`, `aa`, `E`, `I`, `O`, `U`. ReadyPlayerMe/VRM prefix them `viseme_`. Pick one naming per
target engine and rename on export.

**Rhubarb shapes** [29]: A closed (P B M), B slightly open with clenched teeth, C open (EH AE), D wide (AA),
E slightly rounded (AO ER), F puckered (UW OW W), G upper teeth on lower lip (F V), H tongue up (long L),
X rest.

## 3. Our GNM mouth pipeline (human)

TRELLIS has no mouth interior and guessed teeth were rejected, so the mouth comes from a real head model: GNM
(Google, `google/gnm-v3`, Apache 2.0; built from 3D scans, with teeth, gums, tongue, mouth sock and expression
bases). Files live under `$R/tools/gnm`; its sampler runs in `envs/gnm` (Python 3.12 + tensorflow-cpu).

```
c3_face.py  RIGGED.glb  PORTRAIT.png  PORTRAIT_LM.json  OUT.blend        (Blender 5.2)
  ├─ meshfix.py      patch fold-through creases found in plain-white renders
  ├─ paint           portrait → second UV set via 478 MediaPipe landmarks, feathered
  ├─ c4_gnmfit.py    (envs/gnm) fit GNM to the head: 68 landmarks + surface ICP; sample named mouth keys
  └─ c4_mouth.py     swap in GNM lips + a ~20 mm skin band, sock, teeth, tongue: pulled onto the front-most skin
                     by frontal rays, the skin's normals at the seam, seam skin bound to the patch; keys gnm_<name>
c2_anim.py  FACE.blend  LINE.wav  CUES.json  OUTDIR  [FPS] [SIZE]     drive gnm_* from Rhubarb cues + idle
```

- Use the **original flat portrait** as the paint source, not a reconstruction (a reconstruction painted the lips
  skin-coloured).
- Keys (16): `gnm_jaw_open, happy, smile_wide, surprise, snarl, disgust, corners_down, pucker, funneler,
  lips_roll_in, mouth_left, mouth_right, tongue_out, blow, suck, stretch`. All must be 0 at rest (check after save).
- `C3_MOUTH=guess` keeps the old built mouth (`mouth.py`); on 5.x it needs the `Factor` socket fix.
- Gates: fit median ≤ ~1 px on the portrait, GNM landmark error and ICP logged, the seam zipped with matching
  winding, a front check render looked at, close-up sheets (rest, talking, laugh, expressions).
- Hair springs and hair weights fade out near the mouth patch or hair swims through the lips.
- Cats: real teeth and jaw from a licensed skull scan (CC BY), fitted the same way; hiss/snarl from photographs.

## 4. Lip-sync

**Rhubarb** (MIT; the output is yours) [29][30]:

```
$R/tools/Rhubarb-Lip-Sync-1.14.0-Linux/rhubarb -f json --extendedShapes GHX [-d dialog.txt] -o cues.json line.wav
```

`--recognizer pocketSphinx` for English (default) or `phonetic` for other languages; a dialogue file improves
recognition. Rhubarb already inserts tweens (C between A/B and D; E between C/D and F) and anticipates (opens for
an upcoming vowel). Map its shapes onto the mouth set (GNM: jaw + `pucker`/`funneler`/`lips_roll_in`/`smile_wide`).

**Coarticulation** — the mouth is never on one phoneme at a time [27]:
- 40 phonemes map to ~14 visemes; neighbouring repeats merge into one.
- Lip-heavy shapes (OO, OH, W, S, CH) start early and end late; influence can reach up to five phonemes away.
- Onset ~120 ms before the apex; hold the apex to ~75 % of the phoneme; decay over ~120 ms (150 ms for protrusion).
  At 24 fps that is ~3 frames lead.
- Must-hit shapes: M/B/P close the lips (at least 2 frames, closed **before** the sound); F/V lower lip to upper
  teeth. Sounds shorter than a frame do not move the jaw.
- Jaw and lips are separate axes. Do the jaw first, stepped: open big only on stressed syllables, small otherwise.
- Off-sync is a missing preparation, not a global offset.
- Corners never dead-centre; slight asymmetry. Inside a sentence use 40–60 % of a library shape, not 100 %.

**Order of passes** (scenario-labs, MIT): jaw rhythm → mouth corners → shapes → accents → tongue → spline the face.
Eyes dart in 1–2 frames and lead the head; brows change over 3–10 frames.
