**Gameplay Notes — Town Exploration**

**Core Feel**
- Big fantasy town inspired by Ultima IV: top-down grid, cozy and readable.
- WASD movement on the grid; no backend calls for movement.
- Talking is a deliberate action: you press a talk key when you want to converse.

**NPCs and Dialog**
- Many NPCs; dialog is detailed and branching.
- Conversations can reveal keywords or prompts that unlock new dialog elsewhere.
- NPCs can send you across town to fetch objects or talk to other NPCs.

**Movement and Interaction**
- Discrete tile-to-tile movement to keep the U4 feel.
- Separate talk key for deliberate interaction instead of auto-triggering.
- Frontend handles movement and collision checks; backend only sees explicit events.

**Interaction Pattern**
- You move to position near someone, then trigger a talk action.
- Event calls are sent to the backend only when you trigger an interaction.

**Town Scale and Layout**
- Large town layout with multiple districts to encourage wandering.
- Landmarks and unique buildings to make navigation memorable.
- NPC placement supports short errands and cross-town fetch tasks.

**Quest and Dialog Flow**
- Branching dialog with simple, memorable keywords.
- Some NPCs provide direction to other NPCs or locations.
- Fetch tasks are short and readable, designed for quick in-town loops.

**Reference: Ultima IV Feel (Controls)**
- Movement in Ultima IV is grid-based with directional keys (arrow keys). The core feeling is simple tile-to-tile movement. citeturn0search8turn0search7
- Talking is an explicit command in Ultima IV and requires you to choose a direction/target for who you’re talking to. That deliberate “talk” action is part of the vibe to emulate. citeturn0search3turn0search7
