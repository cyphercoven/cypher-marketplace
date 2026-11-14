# Animation craft and realism

PURPOSE: make motion read as alive — the classic principles in numbers we can key, measured human idle and talking
behaviour, and when to go stylised instead.
CONVENTIONS: [n] cites `sources.md` §3. "Derived" frame counts are our arithmetic from the source's milliseconds.
At 24 fps one frame is ~42 ms; at 30 fps ~33 ms.
AGENT NOTES: workflow rules in §1 adapted from scenario-labs/skills (MIT). Everything else is from the cited
primary sources, in our words.

## 1. Workflow

- **Block stepped** (CONSTANT interpolation) and stay stepped long. Key poses, then breakdowns, then in-betweens.
- **Never convert the whole blocking to Bezier at once.** Copy each pose to the end of its hold ("pillars") and
  spline the body only; face and fingers stay stepped until their own pass. (Naive conversion drifted 84 % across a
  hold; pillars drifted 0.) A contact inside continuous motion (a landing) is not a hold — don't pillar it.
- Handle types: AUTO_CLAMPED for holds, AUTO for overshoot/settle, VECTOR for contacts, hits and take-offs.
- Pass order: body → head → arms → face → eyes → secondary (hair, cloth) last.
- Headless: `pose.breakdown` and `pose.blend_to_neighbor` need explicit `prev_frame`/`next_frame`; playblasts are
  Workbench renders. Camera-relative Workbench light: `scene.display.light_direction`.

## 2. The principles, applied (Lasseter 1987 [1], after Thomas & Johnston)

| Principle | What to do | Numbers |
|---|---|---|
| Timing | the number of in-betweens sets weight and mood | a head turn between the same two poses: 0 in-betweens = hit by a huge force; 1 = hit by a brick; 2 = nervous tic; 3 = dodging; 4–10 = progressively calmer [1] |
| Spacing / slow in-out | bunch in-betweens near the extremes | Blender: Bezier (default), Ease In/Out, Back for overshoot [4]; add rest-pose keys either side of a contact to stop spline overshoot [1] |
| Arcs | organic motion travels on arcs; check them in camera pixels | the faster the action, the flatter the arc [1] |
| Anticipation | prepare every action; the faster the action, the clearer the preparation | even a 3–4-frame zip-off gets a readable wind-up [1] |
| Overlap / follow-through | loose parts drag behind and settle after | heavier parts lag further and settle longer; offset parts by 1–2 frames (feet leave 1–2 frames apart; arms move 2 frames after the base lands) [1] |
| Secondary action | supports, never competes | put face changes before or after a big move, not in the middle [1] |
| Squash and stretch | keep volume constant | scale up along the motion, down on the other two axes, aligned to the path [1] |
| Staging | one idea at a time; read it in silhouette | subject ≥ 12 % of frame height (scenario-labs) |
| Exaggeration | balance it; keep a naturalistic baseline | [1] |
| Moving hold | never a dead freeze | overshoot 2 frames and settle back; slow ease into the pose; breath, small head and hip shifts [5][6] |

Working numbers (scenario-labs, MIT): snap after a hold 2–3 frames; hold to read an idea ~6 frames; settle 1–2
frames (4 soft); reaction ~6 frames; head lag 2–3 frames; foot offset 1 frame; gravity at 24 fps 0.01703 m/frame².

## 3. Believable idle and talking (realistic human)

- **Breathing**: 12–18 breaths/min at rest, one cycle every 3.3–5 s [9]. Drive chest/spine rotation and a little
  shoulder lift; never perfectly periodic (add slow noise).
- **Weight shifts**: standing people make fast small "fidgets" about every 50–60 s and shift to a new stance every
  ~3–5 min, with slow drift in between [10]. Hips lead, the head counter-balances.
- **Blinks**: 17/min at rest, 26/min in conversation, 4.5/min while reading or concentrating [11] → idle every
  ~3.5 s, talking every ~2.3 s, irregular. A blink lasts ~⅓ s; closing is faster than opening [12][13] → close in
  2–3 frames, reopen in 4–6 at 24 fps (derived). Blink on head turns and at phrase boundaries.
- **Saccades**: ~3 per second in everyday viewing, 20–80 ms each [15][16]; fixations ~200–250 ms between [17] →
  a 1–2-frame eye snap, then a 6–8-frame hold at 30 fps (derived). Never let the eyes drift smoothly while idle.
- **Eyes lead the head**: in a triggered gaze shift the eyes start 25–40 ms before the head (~1 frame) [19]. Shifts
  under ~20–25° are mostly eyes; larger ones add the head. As the head arrives the eyes counter-rotate to hold the
  target (vestibulo-ocular reflex) [19]. So: eyes snap and land first, head follows and keeps travelling, eyes
  counter-rotate.
- **Gaze while speaking**: speakers look at the listener 20–65 % of the time; they look away at the start of an
  utterance and while thinking, and come back toward the end of the phrase; a turn ends with direct gaze [20].
- **Talking body**: beats on stressed syllables (small head nods, brow lifts) land on or just before the accent,
  never after.

## 4. Stylised vs realistic

| | Realistic (the human) | Stylised (the cats) |
|---|---|---|
| Timing | real-data timing above, mocap where possible, smooth 30 fps | on twos (12 or 15 poses/s), stepped modifier, held poses [7][62] |
| Exaggeration | subtle, balanced against a naturalistic baseline [1] | strong squash and stretch (volume constant), big anticipation |
| Motion blur / smears | real motion blur only | smear frames (1 frame), multiples, motion lines [63] |
| Physics | real gravity, real gait timing | snappier, but keep the real footfall order |

- Blender's **Stepped Interpolation** F-curve modifier holds every N frames ("lowers the curve's frame rate";
  Step Size, Offset) [62]. Constant interpolation gives hard stair-steps [4].
- The SMEAR extension (SIGGRAPH 2024) does elongated in-betweens and motion lines; it is GPL and has a reported
  failure on 5.2.1 [63][64] — test before relying on it.
- **Uncanny valley** (Mori 1970; 2012 IEEE translation [65][66]): affinity rises with human likeness, then drops
  sharply just short of real; movement deepens the valley, and timing matters (a smile slowed to half speed reads
  as creepy). Either commit to real timing everywhere on a realistic face, or stylise clearly. A realistic face with
  stiff or late eyes, mouth or blinks is worse than a stylised one.
