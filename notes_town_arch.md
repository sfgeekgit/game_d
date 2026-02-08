**Goal**
- Town exploration is fast and fully client-side.
- The backend remains the source of truth for any persistent or game-affecting action.
- Town state is generated server-side and validated by the server.

**Core Idea**
- Backend generates a town snapshot (tilemap + NPCs + interactable nodes + allowable events).
- Frontend renders and handles movement locally with no network calls.
- Frontend can only invoke a fixed set of server-approved events (e.g., `talk_npc`, `open_chest`, `enter_building`, `start_encounter`).
- Backend validates each event against the saved town state and returns updates (e.g., NPC dialog progression, chest emptied, new quest flag).

**Data Flow**
1. Client loads town:
- `GET /api/town` returns a full snapshot: map grid, NPC list, interactables, and a list of allowed event IDs.
2. Client moves:
- Movement is simulated entirely in the frontend; no server calls per step.
3. Event is triggered:
- Frontend sends `POST /api/town/event` with `event_id` and optional payload.
4. Server validates:
- Checks event exists, not already consumed, player in correct location context (if needed), then applies changes.
5. Server responds:
- Returns deltas or a new town snapshot (updated NPC states, removed chest, new dialog state).

**Source of Truth Rules**
- Backend stores: generated town seed, immutable layout, NPC identities, active event list, event results, quest flags, and any rewards.
- Frontend stores: transient state only (player position, camera, local animation).
- If the frontend tries an event that isn’t in the allowed list, server rejects it.

**Event Model**
- The town is generated with a limited set of predefined events.
- Triggering an event calls the backend, which decides the outcome.
- The backend tracks which events have happened.

**Why This Meets the Goal**
- Movement feels instant and smooth (no network latency).
- The server remains the authority on anything that changes game state.
- The town can be rebuilt or revalidated server-side since it has the seed and event ledger.

**Tradeoffs / Choices to Decide**
- Do we return full snapshots or delta patches after each event?
- Should events require proof of adjacency? (Client sends player coordinates; server validates against its map).
- Should the client cache the town snapshot with an ETag/version to prevent stale interactions?

**Integration Constraint**
- This should fit into the existing codebase as much as possible.
- Prefer reusing current backend patterns, data access, and content loading.
- Avoid inventing new systems unless the current pieces can’t support the need.
