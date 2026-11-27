# Execution model, context rules and moving files

PURPOSE: how to run Blender with no screen so a job is reproducible, fails loudly and leaves nothing behind.
CONVENTIONS: commands are for Blender 5.2 unless marked 4.2. `$R` is the rig workspace root.
AGENT NOTES: the script contract in §1 is adapted from EL4CTEO/blender-skills (MIT); the context rules in §3
are our own wording of ideas from Blender's lab `blender_mcp` prompts (GPL-3.0, ideas only, nothing copied).

## 1. Running a job

```
LD_LIBRARY_PATH=$R/tools/cuda/lib \
  $R/tools/blender5/blender -b in.blend --factory-startup --python-exit-code 1 -P job.py -- --out /scratch/x
```

- `-b` first. Arguments are processed left to right: the `.blend` before `-P`; for renders the order is file,
  `-P`, `-E`, `-o`, `-F`, then `-f N` or `-a` last.
- `--factory-startup` for reproducible runs (bundled add-ons still load; Rigify does **not** — enable it).
- `--python-exit-code 1` makes a raised exception exit non-zero. Without it `blender -b` exits 0 on a crash.
- `--addons rigify,io_scene_fbx` enables add-ons from the command line.
- Logging changed in 5.0: `--log cycles`, `--log video`, `--log-level` replace `--debug-cycles`, `--debug-ffmpeg`,
  `--verbose`. Do not regex progress lines; the format changes between versions.
- `--background` disables audio. Python 3.13 on 5.1+; user site-packages are not loaded (`--python-use-user-env`
  brings them back). Never pip-install into Blender's Python on a shared box; use a separate env and a subprocess.

**Script contract** (adapted from EL4CTEO, MIT):

```python
import json, sys, traceback
def main(argv):
    ...                                   # do one job, return a dict of evidence
    return {"ok": True, "out": out_path}
try:
    res = main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
except Exception as e:
    res = {"ok": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-2000:]}
print("RESULT " + json.dumps(res)); sys.exit(0 if res.get("ok") else 1)
```

- Record the build in the result: `from bpy import app; app.version_string, app.build_hash`.
- One task per process; long sessions leak memory. Batch runs reset with `bpy.ops.wm.read_factory_settings(use_empty=True)`.
- Never write into the source folder; save copies with `bpy.ops.wm.save_as_mainfile(filepath=..., copy=True)`,
  absolute paths, then reopen and assert what you saved.
- Make scripts idempotent: tag what you create (`ob["cypher_job"] = 1`), reuse it on a rerun, and check that
  `bpy.ops.outliner.orphans_purge(do_recursive=True)` removes nothing new and no owned name has a `.001` twin.
- `bpy.path.abspath("//x")` is relative to the opened `.blend`; use absolute paths in batches.

## 2. Operators vs the data API

Prefer `bpy.data`, `bmesh` and numpy bulk access (`me.vertices.foreach_get("co", buf)` with a float32 buffer).
Operators need the right context and change selection as a side effect. When one is unavoidable:

```python
with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob],
                               selected_editable_objects=[ob]):
    assert bpy.ops.object.modifier_apply(modifier=m.name) == {"FINISHED"}
```

Positional context dicts are gone (`ValueError: 1-2 args execution context is supported`). Some operators
(Rigify generate) want the object **really** selected and active, not only overridden:
`for o in bpy.context.view_layer.objects: o.select_set(False)`, then `ob.select_set(True)`,
`bpy.context.view_layer.objects.active = ob`.

## 3. Context rules (our wording)

- **Mode first.** Many operators do nothing, silently, in the wrong mode. Read `ob.mode`; switch with
  `bpy.ops.object.mode_set(mode=...)` on an active, visible, selectable object; return to OBJECT in `finally`.
- **Active and selected are different.** Set both every time; operators change them. Re-set them between
  consecutive operator calls on different objects.
- **Update before you read.** After moving, posing or changing modifiers, call `bpy.context.view_layer.update()`
  (or `scene.frame_set(f)`) before reading `matrix_world` or evaluated geometry. Evaluated mesh:
  `ev = ob.evaluated_get(dg); me = ev.to_mesh()` … `ev.to_mesh_clear()`.
- **Edit Mode owns the mesh.** In Edit Mode `ob.data` is stale: use `bm = bmesh.from_edit_mesh(me)` and
  `bmesh.update_edit_mesh(me)` (do not free that bmesh), or `ob.update_from_editmode()` before reading.
  Outside Edit Mode: `bm.from_mesh(me)` … `bm.to_mesh(me); me.update(); bm.free()`. Unflushed edits are lost.
- **Object vs data.** Objects and their data are separate datablocks; deleting one leaves the other. Zero-user
  data is dropped on save; give anything you keep a user or `use_fake_user = True`. Check `me.users` before
  editing shared data and make it single-user first.
- **Linked to be seen.** Objects made with the data API must be linked to a collection
  (`bpy.context.collection.objects.link(ob)`). Hidden, excluded-from-view-layer and disabled-for-render are
  three different states; check all three when something "is missing".
- **Rotation mode decides the property.** Writing `rotation_euler` on a `QUATERNION` bone is silently ignored.
- **Spaces.** World vs parent-relative vs object space: use `matrix_world` for world positions; apply scale before
  any geometry-dependent step; set the parent inverse when parenting to keep the visual position.
- **References die.** Re-fetch after `mode_set`, undo, `remove()` or bulk adds; iterate over a `[:]` copy when
  removing; `.copy()` mathutils values you keep; a `Keyframe` reference dies at the next insert on its curve;
  `depsgraph.object_instances` items are valid only inside the loop.
- **Names collide.** Keep the reference returned at creation; never look up by an assumed name; find nodes by
  `type`, not by (localised) name.

## 4. Inspecting the API

```python
node.inputs.keys()                                            # sockets that exist (check .enabled too)
[p.identifier for p in bpy.types.ShaderNodeTexSky.bl_rna.properties]
[(p.identifier, p.type) for p in bpy.ops.object.voxel_remesh.get_rna_type().properties]
try: scene.render.engine = "?"                                # enum lists under-report through RNA:
except TypeError as e: print(e)                               # the error names the accepted values
op.poll()                                                     # before calling an operator
```

(Introspection snippets adapted from Shapedsundew9/tks, MIT.) `hasattr(bpy.types.X, "prop")` does **not** see RNA
properties; test on an instance.

## 5. Moving files through the gateway

Our guests are reached through the gateway, not SSH. The quirks:

- The gateway refuses a command whose command word is a variable, substitution or alias (`$B -b …`,
  `timeout 900 $B …`). Spell the full path every time.
- A command that starts a background job can hold the call open until its timeout; detach with
  `setsid nohup script.sh > log 2>&1 < /dev/null &`, then poll for a marker file.
- Multi-line files: either `echo <base64> | base64 -d > file` (check `sha256sum` afterwards) or write the file in
  the workspace and fetch it with `workspace_download_begin` + `python3 bin/client.py get <URL> <dest>`.
- The first fetch after an edit often fails its sha256 check. Fetch again. Never chain `&&` after a fetch.
- To look at a render, download it (`workspace_download_begin` with the guest as target) and open it; a
  summary of the log is not a look.
