# cypher-mirror on Cowork

Step 4 of `../SKILL.md`: publish the built design system to the artifact store.

1. **Bundle:** `tar -czf ~/scratch/tmp/ds-<key>.tgz -C ds-out <rel>...`, then `workspace_read` with `max_bytes` ≥ the archive size. Decode `content_b64` and `tar -xzf` it under the scratchpad.
2. **Read the store:** Artifact `read`, then Artifact `list` with `scope:"files"`, to see what is published.
3. **Publish:** `root` = the folder containing `project/`; `files = {publishPath: publishPath}`, or `null` for a removed file. At most 255 files per call; send `last` files in a final call.
4. **Tokens changed:** when `project/tokens.json` changed, re-copy each canvas's `fromSystem` entry server-side as `{artifact: <cypherui url>, path: <fromSystem value>}`.
5. **Refused as "not read":** read that artifact once, then retry. A publish refused twice is noted and skipped.
