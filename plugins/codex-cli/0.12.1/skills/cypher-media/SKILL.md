---
name: cypher-media
user-invocable: false
description: Weekly media-library maintenance and the NAS TV-volume watch — stuck downloads, missing episodes and movies, broken files, folders, metadata, specials, free space, and the quarantine clean-up. Use when running or asking about the media maintenance routine, a media download or library problem, or the NAS disk-space check.
---

# cypher-media — weekly library maintenance and the NAS watch

PURPOSE: keep the owner's media library healthy without them. You have the
gateway tools. Find broken files, stuck downloads and missing episodes or movies
that the automation does not fix by itself; grab the best available match even if
it does not fit the quality profile; fix metadata; merge duplicate folders; fix
folder names; and always respect free space. Act — ask only where a rule below
says so.

Every infra fact (guest, paths, volumes, API endpoints, indexers, helper scripts,
vault items) comes from the gateway at run time: `knowledge {topic: <name>}`.
The topics are listed at the end. This skill holds the rules and the order of work.

## When to use

Run this skill for the weekly library maintenance, on demand when a download is
stuck or an episode or movie is missing or broken, or for the NAS TV-volume
disk-space check. The NAS check has its own procedure: open
`references/nas-check.md` for it and do not run it from memory. For a service
fault or a gateway error use **cypher-troubleshoot**; for a credential use
**cypher-secrets**.

**On your host:** read `hosts/<your host>.md` beside this file for how the routine
is started, how its session is labelled and how it notifies.

## Where things are

Ask `knowledge {topic: "media-layout"}` for: the media guest and what runs on it
(the TV and movie managers, the downloader, the indexer manager, the media
server), the four libraries (Shows, anime, Reality TV, movies) with their library
roots on the guest, the NAS volume each lives on, the manager root folders, the
paths the media server sees, the quarantine folders (each holds a `.ignore` file
so the media server skips it — create one with any new quarantine), and the
Reality-routing and library-order cron scripts and their logs.

- "TV" is called **Shows** in logs and summaries.
- Long commands get killed after about two minutes: run long work detached
  (`(setsid nohup … > log 2>&1 < /dev/null &)`) and poll it. Never `pkill -f` a
  pattern that also matches your own command line.
- API access: `knowledge {topic: "media-apis"}` — the local helper on the guest
  first (no tunnel timeout), then the manager APIs from the workspace with keys
  passed through the gateway `secrets:` list and **never printed**. Indexers:
  usenet only; torrent indexers are deliberately off — never enable or use them
  (`knowledge {topic: "media-indexers"}` lists them and the ranked-picker helper).
  Anime: use the ranked picker, not interactive season searches (they time out).
- If you change the live layout, say so in the run log so it can be backfilled
  into git (load **cypher-ops**).
- Keep a run log in the workspace at `~/media-maint/<YYYY-MM-DD>.md` (the write
  tool needs `confirm: true` for that folder). Read last week's log first.

## Guard rails (override everything below)

1. **Space.** Check free space on every NAS volume and on the guest's local data
   disk before grabbing and after. Count what the downloader still has to fetch
   against its target volume. Never grab if the target volume would drop under
   **300 GB** free after the grab. Under **1 TB** free: prefer the smallest
   acceptable release. Cap each run at **150 grabs and 600 GB** total.
2. **Never delete good media.** Allowed deletions only: (a) files proven broken by
   step 5, or folders holding no video, moved first to `<volume>/_quarantine-weekly/<date>/`
   and deleted the following week; (b) broken or failed items removed from a
   manager queue with blocklist; (c) quarantine folders older than 7 days;
   (d) specials (rule 9).
3. **Never restart, redeploy or stop anything public** (media server, request
   app, managers, downloader, indexer manager). Use APIs only. If a fix truly
   needs a restart, notify the owner.
4. **Roll back your own breakage,** then tell them. If the media guest stops
   answering, check its memory pressure from the hypervisor (`pve_node_exec`) and
   stop your own load first.
5. **Load.** The NAS is slow under downloader load. Scan with at most 4 threads,
   `nice -n 19 ionice -c3`, and open files unbuffered (`open(p,'rb',buffering=0)`;
   the default NFS buffer reads 1 MB per file). Skip `*.trickplay`, `_quarantine*`,
   `#recycle`. If the guest still holds a `backup` lock (`pct list` on the node —
   the Sunday backup), do the file scan last.
6. **The owner's deliberate deletions are final.** Before grabbing any missing
   movie or episode, check its manager history. If its file was deleted by hand
   (a file-deleted event with reason Manual, or the file vanished with no failed
   download behind it), do **not** grab it: unmonitor it (movies: remove with an
   import-list exclusion) and log it "skipped — deleted by owner". Never re-add
   anything on the import-exclusion list.
7. **Never accept 3D/SBS or LiNE/CAM/TS releases** (the movie manager parses
   half-SBS as plain Bluray-1080p — read the release name). If one is queued,
   remove it with blocklist and `skipRedownload=true`, then push a 2D or proper
   release. Before removing any queue item, check which series it really belongs
   to: same-titled shows from different countries share a name.
8. **Gateway call fails twice:** note it and move on; notify only if the run could
   not do its job.
9. **No specials, ever.** Never search for or grab Season 0, and never count it as
   missing. Every run, first: set Season 0 `monitored: false` on every series (and
   unmonitor any monitored S00 episodes) — new series from the request app can
   arrive with specials monitored. Remove any queued S00 download
   (`removeFromClient`, blocklist=false). If a series has S00 episode files,
   delete them through the manager (`DELETE /episodefile/bulk`) and move the
   leftover `Specials`/`Season 00` folder (metadata only) to quarantine. Leave the
   fan-edit series alone (`knowledge {topic: "media-layout"}` names it). Log what
   was removed; it is not a reason to ask.

## Each run

1. Begin the session (label and surface: `hosts/<your host>.md`); pass the session
   on every call.
2. Space snapshot (rule 1). Then apply rule 9.
3. **Stuck downloads.** Page through both managers' `/queue`:
   - importPending / importBlocked / importFailed / failedPending, status warning,
     or downloading with no progress for 48 h or more.
   - Obfuscated packs (hash filenames, "Single episode file contains all
     episodes"): map files to episodes by duration against the episode `runtime`,
     by an NFO in the folder, or by the embedded MKV title (search the first
     400 KB for `S01E\d\d`). Import with `GET /manualimport?folder=<container path>`
     (folder only — with `seriesId` it lists the library instead), then
     `POST /command {name: ManualImport, importMode: move, files:[…]}`. Import only
     files you can map without ambiguity; remove the rest with blocklist and
     search per episode.
   - Otherwise `DELETE /queue/{id}?removeFromClient=true&blocklist=true` and
     re-search.
   - Downloader jobs paused for no reason: resume them. Jobs labelled UNWANTED or
     ENCRYPTED: remove with blocklist through the manager and re-search.
   - Remove queue items whose download no longer exists in the downloader.
4. **Missing.** The TV manager's `/wanted/missing` (monitored, aired, season > 0
   only) and the movie manager's movies that are monitored, available and have no
   file and are not queued. Apply rule 6 to every item first.
   - TV: `GET /release?seriesId&seasonNumber` (or per episode); anime: the ranked
     picker. Usenet only.
   - First choice: the best approved release; take a season pack when 4 or more
     episodes of that season are missing.
   - No approved release: take the best rejected one anyway (`POST /release
     {guid, indexerId}`) as long as its only rejections concern quality, profile,
     custom-format score, size or language preference. Never take one that is
     blocklisted, maps to another series or movie, is a sample, is flagged
     dangerous or password-protected, or is below 480p unless nothing else exists.
     Prefer 1080p > 720p > 2160p (size) > 480p; then more grabs; for anime prefer
     dual audio, then English dub, then subs.
   - Respect the caps in rule 1. Log anything unfindable with the reason.
5. **Broken files.** Scan every video file (mkv/mp4/avi/m4v over 1 MB) in all four
   libraries (rule 5): first 4096 bytes all zero = broken. For files modified in
   the last 8 days also run the media server's bundled `ffprobe -v error
   -show_entries format=duration` inside its container, mapping host paths to the
   server's paths (`media-layout`); no duration = broken. For each broken file:
   quarantine it (rule 2a, keep the relative path), `RescanSeries`/`RescanMovie`,
   then `EpisodeSearch`/`MoviesSearch`. More than **50** broken in one week:
   quarantine them and notify the owner — something bigger is wrong.
6. **Folders and metadata** (fix yourself; do not ask):
   - A series whose path is not what `GET /series/{id}/folder` returns (e.g. an
     empty year `()`): if the target folder exists and holds no video, quarantine
     it; then `PUT /series/{id}?moveFiles=true` with the new path and wait for the
     MoveSeries command. The folder format must be `{Series TitleYear}
     [tvdbid-{tvdbid}]` — if it was changed back to `{Year}`, fix it.
   - Duplicate folders in a library with the same tvdbid/tmdbid (movies: also
     compare title + year with `[tmdbid-…]` stripped): keep the one the manager
     points at; quarantine a copy that holds no video; if both hold video, move
     the non-conflicting episodes into the kept folder, quarantine conflicting
     worse copies, then rescan. Also check that a movie's file really is that
     film (a sequel's file can sit under the original's entry).
   - Movies whose path has `()` and whose year is now known: `PUT
     /movie/{id}?moveFiles=true` to `{Movie Title} ({Release Year}) [tmdbid-{TmdbId}]`.
     Announced movies with year 0 stay as they are.
   - Media server: items whose file no longer exists, or any folder moved this
     run, get one `POST /Library/Refresh`. Series or movies with no provider ids,
     no primary image or no overview get `POST /Items/{id}/Refresh?metadataRefreshMode=FullRefresh&imageRefreshMode=FullRefresh&replaceAllMetadata=false&replaceAllImages=false`,
     max 100 per run.
   - Reality TV: same folder checks on its library. Read the routing log; for any
     series logged as over 60 GB, move it **on the NAS** with rsync (about
     150 MB/s against about 12 MB/s over NFS — `knowledge {topic: "media-layout"}`
     gives the host and the helper), then `PUT /series/{id}?moveFiles=false` to
     the new path, rescan, and report it. Confirm the old folder is gone from
     Shows. Also check the media error logs are empty and report anything in them.
   - Do not touch the fan-edit series folder or its metadata.
7. **Clean up:** delete `_quarantine-weekly/` folders older than 7 days. The NAS
   quarantine from the TV-volume watch is deleted only when that task's Plane
   item is Done — see `references/nas-check.md`.
8. **Final check:** every monitored, aired, missing episode (season > 0) or movie
   is either queued in the downloader, logged as unfindable with a reason, or
   skipped as deleted by the owner (rule 6).
9. **Write the log.** Then send ONE notification only if you grabbed, quarantined,
   moved or deleted something, found something only the owner can do, or failed
   (how: `hosts/<your host>.md`). Put the summary in `<routine_summary>` tags,
   lead with one line such as "Media weekly: 12 grabbed, 3 broken replaced, 4
   folders fixed", then the detail: space per volume, grabs (count, GB, how many
   off-profile), skipped as deleted by owner, specials removed, broken files,
   stuck downloads fixed, folders renamed or merged, Reality TV series moved,
   still missing with reasons, and anything that needs them (only a restart or a
   decision you cannot make). If nothing happened, stay silent.

## References — load on demand

| Task | File |
|---|---|
| The NAS TV-volume disk watch: thresholds, verify-then-delete, finish | `references/nas-check.md` |

## Knowledge topics this skill calls

`media-layout` · `media-apis` · `media-indexers` · `nas-tv-watch`. If one answers
"no such topic", say so and stop short of guessing the value.
