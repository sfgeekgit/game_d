**Game Plan — Implementation Status (Completed 2026-02-08)**

**Phase 0 — Core Technical Skeleton**
- [x] `GET /api/town` implemented.
- [x] `POST /api/town/event` implemented.
- [x] Snapshot schema includes `town_id`, `seed`, `width`, `height`, `tiles`, `npcs`, `events`, `allowed_event_ids`, `version`.
- [x] Event validation includes unknown-event rejection, consumed-event handling, adjacency proof, and stale-client version checks.
- [x] Event effects are idempotent for one-time interactions and side-effect-safe for repeatable dialog.
- [x] Content rule enforced: user-facing strings live in `content/ui.json` and `content/dialog/town_dialog.json`.
- [x] Frontend movement is local-only; talk/use triggers backend events.

**Phase 1 — Minimum Slice (Walk Around)**
- [x] Grid-rendered town scene implemented.
- [x] WASD/arrow movement with collision checks implemented.

**Phase 2 — First Event**
- [x] Signpost event implemented and server-validated.
- [x] Event result displayed in frontend dialog/status panel.

**Phase 3 — Item System (Clean DB)**
- [x] `item_types` table implemented.
- [x] `player_items` table implemented.
- [x] Item grants handled by server event logic.

**Phase 4 — Basic NPCs**
- [x] Core branching NPC set implemented (`lyra`, `borin`, `sable`, `quill`, `elowen`).
- [x] Dialog state persisted in `npc_dialog_state`.

**Phase 5 — Town Growth**
- [x] Expanded to 30 NPCs (20 base + 10 cross-town narrative NPCs).
- [x] Dialog content stored in `content/dialog/town_dialog.json`.

**Phase 6 — More Items**
- [x] Added multiple event-driven items: `herb_bundle`, `iron_key`, `market_pass`, `moon_badge`, `sun_ribbon`, `guild_seal`.

**Phase 7 — Cross‑Town Narrative**
- [x] Added second-ring NPC dialog referencing first-ring NPCs and locations.

**Phase 8 — Fetch Quests**
- [x] Implemented short in-town fetch chain:
  - Lyra quest start
  - Herb chest retrieval
  - Lyra turn-in reward
  - Quill archive task
  - Archive retrieval + guild seal completion

**Phase 9 — Hardening / Tech Debt**
- [x] Added backend tests for snapshot shape, adjacency enforcement, stale-client handling, idempotent one-time events, item/flag progression.
- [x] Added frontend tests for load path, no-network movement behavior, and talk interaction event POST.

**Implementation Files**
- Backend core: `backend/game/town.py`
- API views: `backend/game/views.py`
- API routes: `backend/game/urls.py`
- Frontend scene: `frontend/src/App.jsx`
- Frontend styling: `frontend/src/index.css`
- Content text: `content/ui.json`, `content/dialog/town_dialog.json`, `content/story/town_story.json`
- Tests: `backend/game/tests.py`, `frontend/src/App.test.jsx`
