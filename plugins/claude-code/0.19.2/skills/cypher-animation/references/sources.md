# Sources and licences

PURPOSE: what this skill took from where, under which licence, and every source behind a number or claim.
CONVENTIONS: licences were read from each repository's own LICENSE file on 2026-11-01 at the commit listed.
"Adapted" = short code or text reused with attribution (MIT); "ideas only" = rewritten in our words, nothing copied.
AGENT NOTES: before adding material from a new source, read its LICENSE file and add a row here first.

## 1. Skill sources

| Source | Commit read | Licence | Copyright | Used for | How |
|---|---|---|---|---|---|
| github.com/EL4CTEO/blender-skills | fb92cfb4cc5a | MIT | Copyright (c) 2026 EL4CTEO | script contract, Rigify build, bind with voxel-proxy fallback, shape-key split/report/drivers, slotted-action and bake recipes, render presets, 5.x table rows | adapted |
| github.com/scenario-labs/skills (`skills/dcc/blender/*`) | 7f4b801c7248 | MIT | Copyright (c) 2026 Scenario Inc. | joint placement and landmarks, metarig-is-the-source, silent auto-weight failure, voxel schedule, deformation gates, blocking/pillars, lip-sync passes, timing numbers, headless limits | adapted |
| github.com/Shapedsundew9/tks (`blender-bpy-5x`) | f0ae68aa875a | MIT (repo); vendored guides MIT | Copyright (c) 2026 Shaped Sundew; guides Copyright (c) 2025 Siddharth Ahuja | 4.x→5.x traps table, "inspect the API, don't guess", introspection snippets | adapted |
| github.com/RobLe3/cc-blender-skill | a2634b588e80 | MIT | Copyright (c) 2026 RobLe3 | F-curve compatibility approach, driver/NLA recipes and which work headless | adapted (our own slot-correct helper) |
| projects.blender.org/lab/blender_mcp (`prompts.yml`) | dbbf836ad4b1 | GPL-3.0-or-later | Blender Authors | context rules: mode, active vs selected, depsgraph update, bmesh flush, datablocks, rotation mode | **ideas only**, rewritten |
| Google GNM head (`google/gnm-v3`) | — | Apache 2.0 | Google | real mouth interior and expression bases in our pipeline | used as a model asset |
| Rhubarb Lip Sync (github.com/DanielSWolf/rhubarb-lip-sync) | 1.14.0 | MIT; output belongs to the user | Daniel S. Wolf | lip-sync cues | tool |

MIT licence notice for the adapted material (applies to each MIT copyright line above):

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
> documentation files (the "Software"), to deal in the Software without restriction, including without limitation
> the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
> permit persons to whom the Software is furnished to do so, subject to the following conditions: The above
> copyright notice and this permission notice shall be included in all copies or substantial portions of the
> Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
> LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
> SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
> OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
> DEALINGS IN THE SOFTWARE.

## 2. Our own measurements

- `api-4x-5x.md` §1: probe and side-by-side runs of our scripts on Blender 4.2.23 LTS and 5.2.3 LTS, 2026-11-01.
- Blender 5.2.3 LTS is the current stable release (blender.org download page, released 2026-10-22).

## 3. Cited works (numbers match the [n] markers)

1. Lasseter, J. "Principles of Traditional Animation Applied to 3D Computer Animation." SIGGRAPH Computer Graphics 21(4):35–44, 1987. DOI 10.1145/37402.37407
4. Blender Manual, Graph Editor › F-Curves › Properties (interpolation, easing). docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/properties.html
5. Animation Mentor, "What is a moving hold?" (newsletter).
6. Animation Mentor blog, "Why all animators need to master the moving hold".
7. Persichetti, B., on animating *Spider-Man: Into the Spider-Verse* "on twos" (/Film interview).
8. Blender Manual, Render › Output › Format (frame rate = FPS / Base).
9. Cleveland Clinic, "Vital Signs" (adult resting respiratory rate 12–18/min).
10. Duarte, M. & Zatsiorsky, V. M. "Patterns of center of pressure migration during prolonged unconstrained standing." Motor Control 3(1):12–27, 1999.
11. Bentivoglio, A. R. et al. "Analysis of blink rate patterns in normal subjects." Movement Disorders 12(6), 1997. PMID 9399231
12. Kwon, K.-A. et al. Blink kinematics with a high-speed camera. J. R. Soc. Interface, 2013.
13. Spontaneous blinking, optoelectronic study (closing faster than opening). PMID 18565090
15. "Vision as oculomotor reward…", Cognitive Neurodynamics, 2021. PMC8286912
16. "Saccades and driving", Acta Otorhinolaryngol Ital, 2019. PMC6536025
17. Rayner, K. "Eye movements in reading and information processing: 20 years of research." Psychol Bull, 1998. PMID 9849112
19. Freedman, E. G. "Coordination of the eyes and head during visual orienting." Exp Brain Res 190(4):369–387, 2008. PMC2605952
20. Ho, S., Foulsham, T. & Kingstone, A. "Speaking and listening with the eyes: gaze signaling during dyadic interactions." PLoS ONE 10(8):e0136905, 2015. PMC4550266
21. Paul Ekman Group, Facial Action Coding System (Ekman & Friesen 1978; rev. 2002).
22. Apple Developer Documentation (developer.apple.com), ARKit › `ARFaceAnchor` › `BlendShapeLocation`.
24. Ozel, M. "ARKit to FACS cheat sheet" (community reference; not Apple).
26. Google AI Edge, MediaPipe Face Landmarker (blendshape output). developers.google.com/edge/mediapipe/solutions/vision/face_landmarker
27. Edwards, P. et al. "JALI: An Animator-Centric Viseme Model for Expressive Lip Synchronization." ACM TOG 35(4), SIGGRAPH 2016. DOI 10.1145/2897824.2925984
29. Rhubarb Lip Sync README. github.com/DanielSWolf/rhubarb-lip-sync
30. Rhubarb Lip Sync LICENSE (MIT). github.com/DanielSWolf/rhubarb-lip-sync
31. Carnegie Mellon University Graphics Lab Motion Capture Database, terms of use. mocap.cs.cmu.edu
32. Adobe, Mixamo FAQ. helpx.adobe.com/creative-cloud/faq/mixamo-faq.html
33. Adobe Community, Mixamo licensing FAQ (2022, community answer); Adobe General Terms of Use.
34. Bandai Namco Research Motiondataset README (CC BY-NC 4.0). github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset
35. AMASS licence. amass.is.tue.mpg.de/license.html
36. SMPL-Body licence (CC BY 4.0). smpl.is.tue.mpg.de/license.html
37. SMPL-Model licence. smpl.is.tue.mpg.de/modellicense.html
38. SMPL-X model licence. smpl-x.is.tue.mpg.de/modellicense.html
39. Rokoko, free mocap assets. www.rokoko.com/mocap/free-mocap-assets
40. Blender Manual, Animation › Armatures › Skinning › Introduction (retargeting via add-ons).
41. Blender Manual, Import/Export › Motion Capture (BVH). docs.blender.org/manual/en/latest/files/import_export/bvh.html
43. Rokoko Studio Live for Blender. github.com/Rokoko/rokoko-studio-live-blender
44. Expy Kit. github.com/pKrime/Expy-Kit
45. "Retarget" extension. extensions.blender.org/add-ons/retarget/
46. Auto-Rig Pro (Artell), product page.
47. GVHMR. github.com/zju3dv/GVHMR
48. WHAM. github.com/yohanshin/WHAM
49. 4D-Humans. github.com/shubham-goel/4D-Humans
50. SMPLer-X. github.com/caizhongang/SMPLer-X
51. FreeMoCap. github.com/freemocap/freemocap
52. SAM 3D Body. github.com/facebookresearch/sam-3d-body
53. MHR body model. github.com/facebookresearch/MHR
54. Cartmill, M., Lemelin, P. & Schmitt, D. "Support polygons and symmetrical gaits in mammals." Zool J Linn Soc 136, 2002.
55. Bishop, K. L., Pai, A. K. & Schmitt, D. "Whole Body Mechanics of Stealthy Walking in Cats." PLoS ONE, 2008. DOI 10.1371/journal.pone.0003808, PMC2583958
56. Afelt, Z. & Kasicki, S. Cat and dog locomotion. Acta Neurobiol Exp, 1975.
57. Biancardi, C. M. & Minetti, A. E. "Biomechanical determinants of transverse and rotary gallop in cursorial mammals." J Exp Biol 215, 2012.
58. Blender Manual (docs.blender.org), Add-ons › Rigify › Basic Usage (metarig list; 1 unit = 1 m).
59. Blender Manual (docs.blender.org), Add-ons › Rigify (bundled with Blender).
60. National Gallery of Art, Muybridge, Plate 720 "Cat; galloping" (Open Access, public domain). www.nga.gov/artworks/220472-plate-number-720-cat-galloping
61. National Gallery of Art, Muybridge, Plate 716 "Cat; walking; change to galloping". www.nga.gov/artworks/220470-plate-number-716-cat-walking-change-galloping
62. Blender Manual, Graph Editor › F-Curve Modifiers (Stepped Interpolation). docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/modifiers.html
63. Basset, J., Bénard, P. & Barla, P. "SMEAR: Stylized Motion Exaggeration with ARt-direction." SIGGRAPH 2024. DOI 10.1145/3641519.3657457; code github.com/MoStyle/SMEAR
64. SMEAR extension listing (GPL-3+). extensions.blender.org/add-ons/smear/
65. Mori, M. "The Uncanny Valley." Energy 7(4):33–35, 1970; trans. MacDorman, K. F. & Kageki, N., IEEE Robotics & Automation Magazine 19(2):98–100, 2012.
66. DOI 10.1109/MRA.2012.2192811 (the 2012 translation).

Not verified at the source (do not treat as fact without checking): a frame count for how long a still hold lasts
before it "dies"; a primary study of spontaneous-blink duration; Mixamo's own wording on redistribution and ML
training; the MediaPipe face model licence; VRAM needs of the video-to-motion tools on a 16 GB card.
