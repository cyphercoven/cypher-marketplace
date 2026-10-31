# NAS TV-volume disk watch

PURPOSE: keep the TV volume from filling while replacement episodes download, free
space from the quarantined broken files when needed, and delete the quarantine once
every replacement is in and verified.

Rules (the owner approved the deletions below in advance: when all are replaced and
verified, delete the quarantine regardless):

- Facts come from `knowledge {topic: "nas-tv-watch"}`: the TV volume and its mount on
  the media guest, the quarantine folder and its `MANIFEST.txt`, the TV manager's API
  address and secret item, the plan file of episodes to replace (fields: series id,
  episode id, series, season, episode), the media server's ffprobe path, and the Plane
  item that tracks this job (project, item id, comment endpoint). Never guess them.
- Never delete anything outside that quarantine folder, except bad replacement files
  through the TV manager (step 5).
- Never restart anything public. A gateway call that fails twice: notify the owner
  with the tool and the error, and stop.

## Each run

1. Begin the session (label "Cypher: ops: TV disk watch"; surface: `hosts/<your host>.md`)
   and pass it on every call.
2. On the media guest: `df -BG <tv mount> | tail -1` and `du -sh` on the quarantine and
   downloads folders. Keep commands short (NFS; `timeout 300`). If the quarantine
   folder no longer exists the job is finished: say so in one line, disable the
   recurring task (`hosts/<your host>.md`) and stop.
3. TV manager: classify every plan episode as has-file, still in the queue (`/queue`
   paged, by episode id), or neither. For "neither", run one `EpisodeSearch` for them
   (once per run).
4. Space rules:
   - Free on the TV volume ≥ **400 GB**: no space action.
   - Free < 400 GB: delete from the quarantine only files whose episode now has a file
     in the manager (quarantined path = quarantine folder + the original path minus
     the library prefix). Re-check `df`.
   - Still < **250 GB**: delete the whole quarantine folder. Re-check `df`.
   - Still < **150 GB** with the quarantine gone: delete nothing else; notify the owner
     with free space and what is using it, and ask what to remove.
5. Finish — only when EVERY plan episode has a file. Verify the new files first: for
   each episode get its file path from the manager (`/episodefile/{id}`), map it to the
   guest path, and check the first 4096 bytes are not all zero
   (`head -c 4096 f | tr -d '\0' | wc -c` > 0) and that the media server's `ffprobe -v
   error -show_entries format=duration` returns a duration. Do it in one batched script
   on the guest (path list on stdin), not one call per file.
   - All verified: remove the quarantine folder, re-check `df`, comment the final tally
     and GB freed on the Plane item, set it Done, send the owner one notification
     ("TV replacement complete: N episodes verified, quarantine deleted, X GB freed"),
     then disable the recurring task (never delete it — a session cannot delete the
     task that started it).
   - Any fail: keep the quarantine copies of the failed ones; delete the bad new file
     through the manager (`DELETE /episodefile/{id}`), run `EpisodeSearch`, comment
     which on the Plane item, and continue next run.
6. Whenever you delete anything, comment on the Plane item (what, GB freed, new free
   space). Notify the owner only for: a deletion forced by low space, the finish, or a
   failure. Otherwise stay silent and end with a one-line summary.
