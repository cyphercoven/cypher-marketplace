# Animals (cats first)

PURPOSE: rig and move quadrupeds from real anatomy and real gait data, not from a human rig bent over.
CONVENTIONS: [n] cites `sources.md` §3. Blender 5.2; Rigify must be enabled.
AGENT NOTES: our cats are stylised in look; keep their footfall order and weight real (`craft-and-realism.md` §4).

## 1. Rig

```python
import addon_utils; addon_utils.enable("rigify", default_set=True, persistent=False)
bpy.ops.object.armature_cat_metarig_add()     # also basic_quadruped, wolf, horse
```

- Rigify ships Cat, Wolf, Horse and Basic Quadruped metarigs (also Bird and Shark) [58][59]; probed on our 4.2 and 5.2
  builds. Rigify assumes 1 unit = 1 m; scale the metarig to the mesh, then place joints by hand.
- Place joints from anatomy, not proportion: shoulder blade (scapula) slides on the ribcage, so the front leg's top
  joint sits high and behind the elbow; the hind leg's "backward knee" is the ankle (hock); cats walk on their toes
  (digitigrade), so the paw contact is the toe pads and the heel never touches.
- Spine: enough bones for the arch and twist (stalk, pounce, groom); tail as a chain with follow-through.
- Faces: ears (back/forward/flat), lids, jaw, whiskers as shape keys or bones; our cat face script builds
  `ear_*`, `lid_*`, `jaw_open`, `whisker_*` keys. Real teeth and jaw come from a licensed skull scan, not a guess.
- Weights: same silent-failure checks as humans (`rigging.md` §4); fur cards get weights by applied transfer.

## 2. Gaits

- **Duty factor** = stance time / stride. Walk > 50 % (at least two feet down); run < 50 % with an airborne phase [54].
- **Walk**: lateral sequence, LH → LF → RH → RF, used by most mammals [54]. Diagonality D = % of the cycle by which
  the left hind footfall precedes the left fore; D = 50 is a walking trot, 0/100 a pace [54].
- **Cats**: walk → trot transition near 1 m/s (Froude 0.5) [55]; crouched, stalking walks use more evenly spaced
  footfalls (higher diagonality) and a compliant, low body [55]. Walk ~1–4 km/h, trot ~3.5–8 km/h, gallop from
  ~8 km/h; gallop stance 120–140 ms, swing 180–300 ms [56].
- **Gallop**: felids gallop **rotary** only (second hind foot followed by the same-side fore foot), duty factor
  ~23 % [57]; horses use transverse. The spine flexes and extends with each stride.
- Head and tail counter the body: the head bobs least in a walk, the tail lags and overshoots.
- Keep the root moving linearly across a cycle (REPEAT_OFFSET); plant feet with pins (no slide).

## 3. Reference footage

- Muybridge, *Animal Locomotion* (1887): e.g. Plate 716 "Cat; walking; change to galloping", Plate 720 "Cat;
  galloping"; public domain via the National Gallery of Art [60][61]. Step through frame by frame and copy contact
  timing and spine shape.
- Own footage of the real cats: film side-on at a known frame rate, count frames between contacts, and key from it.
- For expressions (hiss, snarl, ears flat) work from photographs of the real behaviour, not imagination.
