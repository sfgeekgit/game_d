import hashlib
import json
import uuid

from . import db

TOWN_WIDTH = 32
TOWN_HEIGHT = 20

PASSABLE_TILES = {"G", "P", "B"}

NPCS = [
    {"npc_id": "npc_lyra", "name_key": "npc.npc_lyra", "x": 6, "y": 3},
    {"npc_id": "npc_borin", "name_key": "npc.npc_borin", "x": 10, "y": 4},
    {"npc_id": "npc_sable", "name_key": "npc.npc_sable", "x": 14, "y": 4},
    {"npc_id": "npc_quill", "name_key": "npc.npc_quill", "x": 20, "y": 4},
    {"npc_id": "npc_elowen", "name_key": "npc.npc_elowen", "x": 24, "y": 4},
    {"npc_id": "npc_tarin", "name_key": "npc.npc_tarin", "x": 7, "y": 8},
    {"npc_id": "npc_mara", "name_key": "npc.npc_mara", "x": 11, "y": 8},
    {"npc_id": "npc_nessa", "name_key": "npc.npc_nessa", "x": 15, "y": 8},
    {"npc_id": "npc_oswin", "name_key": "npc.npc_oswin", "x": 19, "y": 8},
    {"npc_id": "npc_pru", "name_key": "npc.npc_pru", "x": 23, "y": 8},
    {"npc_id": "npc_ren", "name_key": "npc.npc_ren", "x": 27, "y": 8},
    {"npc_id": "npc_selin", "name_key": "npc.npc_selin", "x": 5, "y": 12},
    {"npc_id": "npc_tovan", "name_key": "npc.npc_tovan", "x": 9, "y": 12},
    {"npc_id": "npc_ursa", "name_key": "npc.npc_ursa", "x": 13, "y": 12},
    {"npc_id": "npc_vann", "name_key": "npc.npc_vann", "x": 17, "y": 12},
    {"npc_id": "npc_wren", "name_key": "npc.npc_wren", "x": 21, "y": 12},
    {"npc_id": "npc_xara", "name_key": "npc.npc_xara", "x": 25, "y": 12},
    {"npc_id": "npc_yorik", "name_key": "npc.npc_yorik", "x": 28, "y": 12},
    {"npc_id": "npc_zev", "name_key": "npc.npc_zev", "x": 4, "y": 16},
    {"npc_id": "npc_aela", "name_key": "npc.npc_aela", "x": 8, "y": 16},
    {"npc_id": "npc_brinn", "name_key": "npc.npc_brinn", "x": 12, "y": 16},
    {"npc_id": "npc_cass", "name_key": "npc.npc_cass", "x": 16, "y": 16},
    {"npc_id": "npc_dane", "name_key": "npc.npc_dane", "x": 20, "y": 16},
    {"npc_id": "npc_eris", "name_key": "npc.npc_eris", "x": 24, "y": 16},
    {"npc_id": "npc_fenn", "name_key": "npc.npc_fenn", "x": 28, "y": 16},
    {"npc_id": "npc_galen", "name_key": "npc.npc_galen", "x": 6, "y": 18},
    {"npc_id": "npc_hale", "name_key": "npc.npc_hale", "x": 10, "y": 18},
    {"npc_id": "npc_iora", "name_key": "npc.npc_iora", "x": 14, "y": 18},
    {"npc_id": "npc_jory", "name_key": "npc.npc_jory", "x": 18, "y": 18},
    {"npc_id": "npc_kipp", "name_key": "npc.npc_kipp", "x": 22, "y": 18},
]

INTERACTABLE_EVENTS = [
    {"event_id": "read_sign_gate", "type": "read_sign", "x": 3, "y": 2, "repeatable": True},
    {"event_id": "read_sign_plaza", "type": "read_sign", "x": 16, "y": 10, "repeatable": True},
    {"event_id": "open_chest_herb", "type": "open_chest", "x": 27, "y": 3, "repeatable": False},
    {"event_id": "open_chest_archive", "type": "open_chest", "x": 28, "y": 14, "repeatable": False},
    {"event_id": "enter_hall", "type": "enter_building", "x": 2, "y": 10, "repeatable": True},
    {"event_id": "enter_guild", "type": "enter_building", "x": 30, "y": 10, "repeatable": True},
]

ITEM_TYPES = [
    {
        "item_id": "herb_bundle",
        "name_key": "item.herb_bundle.name",
        "description_key": "item.herb_bundle.description",
        "tags": "quest,herb",
    },
    {
        "item_id": "iron_key",
        "name_key": "item.iron_key.name",
        "description_key": "item.iron_key.description",
        "tags": "quest,key",
    },
    {
        "item_id": "market_pass",
        "name_key": "item.market_pass.name",
        "description_key": "item.market_pass.description",
        "tags": "quest,pass",
    },
    {
        "item_id": "moon_badge",
        "name_key": "item.moon_badge.name",
        "description_key": "item.moon_badge.description",
        "tags": "quest,reward",
    },
    {
        "item_id": "sun_ribbon",
        "name_key": "item.sun_ribbon.name",
        "description_key": "item.sun_ribbon.description",
        "tags": "quest,archive",
    },
    {
        "item_id": "guild_seal",
        "name_key": "item.guild_seal.name",
        "description_key": "item.guild_seal.description",
        "tags": "quest,reward",
    },
]

NPC_DIALOG_PATHS = {
    "npc_lyra": ["intro", "quest_start", "quest_wait", "quest_done"],
    "npc_borin": ["intro", "forge_key", "forge_after"],
    "npc_sable": ["intro", "needs_key", "grant_pass", "after_pass"],
    "npc_quill": ["intro", "task_start", "task_wait", "task_done"],
    "npc_elowen": ["intro", "cross_town", "cross_town_after"],
}

GENERIC_DIALOG = ["hello", "rumor", "direction"]


def ensure_schema():
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS user_login (
            user_id CHAR(36) NOT NULL PRIMARY KEY,
            name VARCHAR(100) DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            user_id CHAR(36) NOT NULL PRIMARY KEY,
            points BIGINT NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS player_towns (
            user_id CHAR(36) NOT NULL PRIMARY KEY,
            town_id VARCHAR(64) NOT NULL,
            seed BIGINT NOT NULL,
            version INT NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS player_event_ledger (
            user_id CHAR(36) NOT NULL,
            event_id VARCHAR(100) NOT NULL,
            result_json LONGTEXT NOT NULL,
            applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, event_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS player_flags (
            user_id CHAR(36) NOT NULL,
            flag VARCHAR(100) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, flag)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS item_types (
            item_id VARCHAR(50) NOT NULL PRIMARY KEY,
            name_key VARCHAR(120) NOT NULL,
            description_key VARCHAR(120) NOT NULL,
            tags VARCHAR(120) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS player_items (
            user_id CHAR(36) NOT NULL,
            item_id VARCHAR(50) NOT NULL,
            qty INT NOT NULL DEFAULT 0,
            acquired_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, item_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS npc_dialog_state (
            user_id CHAR(36) NOT NULL,
            npc_id VARCHAR(60) NOT NULL,
            node_index INT NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, npc_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    for item in ITEM_TYPES:
        db.execute(
            """
            INSERT IGNORE INTO item_types (item_id, name_key, description_key, tags)
            VALUES (%s, %s, %s, %s)
            """,
            [item["item_id"], item["name_key"], item["description_key"], item["tags"]],
        )


def get_or_create_user(session):
    user_id = session.get("user_id")
    if user_id:
        row = db.fetch_one("SELECT user_id FROM user_login WHERE user_id = %s", [user_id])
        if row:
            return user_id, False

    user_id = str(uuid.uuid4())
    db.execute("INSERT INTO user_login (user_id) VALUES (%s)", [user_id])
    db.execute("INSERT INTO players (user_id, points) VALUES (%s, 0)", [user_id])
    session["user_id"] = user_id
    return user_id, True


def user_data(user_id):
    row = db.fetch_one(
        "SELECT ul.user_id, ul.name, ul.created_at, p.points "
        "FROM user_login ul JOIN players p ON ul.user_id = p.user_id WHERE ul.user_id = %s",
        [user_id],
    )
    if not row:
        return None
    return {
        "user_id": row[0],
        "name": row[1],
        "created_at": row[2].isoformat() if row[2] else None,
        "points": row[3],
    }


def _event_catalog():
    events = {}
    for npc in NPCS:
        event_id = f"talk_{npc['npc_id']}"
        events[event_id] = {
            "event_id": event_id,
            "type": "talk_npc",
            "x": npc["x"],
            "y": npc["y"],
            "repeatable": True,
            "npc_id": npc["npc_id"],
        }
    for evt in INTERACTABLE_EVENTS:
        events[evt["event_id"]] = evt
    return events


def _build_tiles(seed):
    # Seed is reserved for future procedural decoration and serialized in snapshot.
    _ = seed
    rows = []
    for y in range(TOWN_HEIGHT):
        chars = []
        for x in range(TOWN_WIDTH):
            if x == 0 or y == 0 or x == TOWN_WIDTH - 1 or y == TOWN_HEIGHT - 1:
                chars.append("W")
            elif y in (6, 10, 14) or x in (8, 16, 24):
                chars.append("P")
            elif 12 <= x <= 14 and 1 <= y <= 5:
                chars.append("W")
            elif 25 <= x <= 30 and 12 <= y <= 15:
                chars.append("W")
            elif 2 <= x <= 5 and 9 <= y <= 11:
                chars.append("W")
            else:
                chars.append("G")
        rows.append("".join(chars))

    # Bridge entrances (passable openings) for halls.
    rows[10] = rows[10][:2] + "B" + rows[10][3:30] + "B" + rows[10][31:]
    return rows


def _ensure_player_town(user_id):
    row = db.fetch_one(
        "SELECT town_id, seed, version FROM player_towns WHERE user_id = %s",
        [user_id],
    )
    if row:
        return {"town_id": row[0], "seed": int(row[1]), "version": int(row[2])}

    seed = int(hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12], 16)
    town_id = f"town-{seed % 1000000:06d}"
    db.execute(
        "INSERT INTO player_towns (user_id, town_id, seed, version) VALUES (%s, %s, %s, 1)",
        [user_id, town_id, seed],
    )
    return {"town_id": town_id, "seed": seed, "version": 1}


def _get_flags(user_id):
    rows = db.fetch_all("SELECT flag FROM player_flags WHERE user_id = %s", [user_id])
    return {row[0] for row in rows}


def _add_flag(user_id, flag):
    return db.execute(
        "INSERT IGNORE INTO player_flags (user_id, flag) VALUES (%s, %s)",
        [user_id, flag],
    )


def _get_items(user_id):
    rows = db.fetch_dicts(
        "SELECT pi.item_id, pi.qty, it.name_key, it.description_key, it.tags "
        "FROM player_items pi JOIN item_types it ON pi.item_id = it.item_id "
        "WHERE pi.user_id = %s AND pi.qty > 0 ORDER BY pi.item_id",
        [user_id],
    )
    items = []
    for row in rows:
        items.append(
            {
                "item_id": row["item_id"],
                "qty": int(row["qty"]),
                "name_key": row["name_key"],
                "description_key": row["description_key"],
                "tags": row["tags"],
            }
        )
    return items


def _has_item(user_id, item_id, qty=1):
    row = db.fetch_one(
        "SELECT qty FROM player_items WHERE user_id = %s AND item_id = %s",
        [user_id, item_id],
    )
    return bool(row and int(row[0]) >= qty)


def _grant_item(user_id, item_id, qty=1):
    db.execute(
        """
        INSERT INTO player_items (user_id, item_id, qty)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE qty = qty + VALUES(qty)
        """,
        [user_id, item_id, qty],
    )


def _consume_item(user_id, item_id, qty=1):
    db.execute(
        "UPDATE player_items SET qty = GREATEST(0, qty - %s) WHERE user_id = %s AND item_id = %s",
        [qty, user_id, item_id],
    )


def _get_dialog_index(user_id, npc_id):
    row = db.fetch_one(
        "SELECT node_index FROM npc_dialog_state WHERE user_id = %s AND npc_id = %s",
        [user_id, npc_id],
    )
    return int(row[0]) if row else 0


def _set_dialog_index(user_id, npc_id, index):
    db.execute(
        """
        INSERT INTO npc_dialog_state (user_id, npc_id, node_index)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE node_index = VALUES(node_index)
        """,
        [user_id, npc_id, index],
    )


def _is_passable(x, y, tiles):
    if x < 0 or y < 0 or y >= len(tiles) or x >= len(tiles[0]):
        return False
    return tiles[y][x] in PASSABLE_TILES


def _town_snapshot(user_id):
    town = _ensure_player_town(user_id)
    tiles = _build_tiles(town["seed"])
    events = _event_catalog()

    consumed_rows = db.fetch_all(
        "SELECT event_id FROM player_event_ledger WHERE user_id = %s",
        [user_id],
    )
    consumed = {row[0] for row in consumed_rows}

    event_list = []
    allowed = []
    for event in events.values():
        is_consumed = (event["event_id"] in consumed) and (not event.get("repeatable", False))
        state = "consumed" if is_consumed else "available"
        event_list.append(
            {
                "event_id": event["event_id"],
                "type": event["type"],
                "state": state,
                "pos": {"x": event["x"], "y": event["y"]},
            }
        )
        if state == "available":
            allowed.append(event["event_id"])

    flags = sorted(_get_flags(user_id))
    items = _get_items(user_id)

    npcs = []
    for npc in NPCS:
        npcs.append(
            {
                "npc_id": npc["npc_id"],
                "name_key": npc["name_key"],
                "pos": {"x": npc["x"], "y": npc["y"]},
                "event_ids": [f"talk_{npc['npc_id']}"] ,
            }
        )

    return {
        "town_id": town["town_id"],
        "seed": town["seed"],
        "width": TOWN_WIDTH,
        "height": TOWN_HEIGHT,
        "tiles": tiles,
        "npcs": npcs,
        "events": sorted(event_list, key=lambda e: e["event_id"]),
        "allowed_event_ids": sorted(allowed),
        "version": town["version"],
        "player_state": {
            "flags": flags,
            "items": items,
        },
    }


def get_town_snapshot(user_id):
    return _town_snapshot(user_id)


def _bump_version(user_id):
    db.execute(
        "UPDATE player_towns SET version = version + 1 WHERE user_id = %s",
        [user_id],
    )


def _record_event(user_id, event_id, result):
    db.execute(
        "INSERT INTO player_event_ledger (user_id, event_id, result_json) VALUES (%s, %s, %s)",
        [user_id, event_id, json.dumps(result)],
    )


def _load_recorded_event(user_id, event_id):
    row = db.fetch_one(
        "SELECT result_json FROM player_event_ledger WHERE user_id = %s AND event_id = %s",
        [user_id, event_id],
    )
    if not row:
        return None
    return json.loads(row[0])


def _validate_adjacency(event, payload, snapshot):
    player = payload.get("player_position") or {}
    target = payload.get("target_position") or {}

    try:
        px = int(player.get("x"))
        py = int(player.get("y"))
        tx = int(target.get("x"))
        ty = int(target.get("y"))
    except (TypeError, ValueError):
        return False

    if tx != event["x"] or ty != event["y"]:
        return False

    if abs(px - tx) + abs(py - ty) != 1:
        return False

    if not _is_passable(px, py, snapshot["tiles"]):
        return False

    return True


def _generic_npc_event(user_id, npc_id):
    path = NPC_DIALOG_PATHS.get(npc_id, GENERIC_DIALOG)
    idx = _get_dialog_index(user_id, npc_id)
    node = path[idx % len(path)]
    _set_dialog_index(user_id, npc_id, (idx + 1) % len(path))
    return {
        "message_key": f"dialog.{npc_id}.{node}",
        "flags_added": [],
        "items_added": [],
    }


def _special_npc_event(user_id, npc_id):
    flags = _get_flags(user_id)

    if npc_id == "npc_lyra":
        if "herb_quest_started" not in flags:
            _add_flag(user_id, "herb_quest_started")
            return {
                "message_key": "event.lyra.quest_start",
                "flags_added": ["herb_quest_started"],
                "items_added": [],
            }
        if "herb_collected" in flags and "herb_turned_in" not in flags and _has_item(user_id, "herb_bundle"):
            _consume_item(user_id, "herb_bundle", 1)
            _grant_item(user_id, "moon_badge", 1)
            _add_flag(user_id, "herb_turned_in")
            return {
                "message_key": "event.lyra.quest_complete",
                "flags_added": ["herb_turned_in"],
                "items_added": ["moon_badge"],
            }
        if "herb_turned_in" in flags:
            return {
                "message_key": "event.lyra.after_quest",
                "flags_added": [],
                "items_added": [],
            }
        return {
            "message_key": "event.lyra.quest_wait",
            "flags_added": [],
            "items_added": [],
        }

    if npc_id == "npc_borin":
        if "iron_key_given" not in flags:
            _grant_item(user_id, "iron_key", 1)
            _add_flag(user_id, "iron_key_given")
            return {
                "message_key": "event.borin.key_given",
                "flags_added": ["iron_key_given"],
                "items_added": ["iron_key"],
            }
        return {"message_key": "event.borin.after", "flags_added": [], "items_added": []}

    if npc_id == "npc_sable":
        if "market_pass_given" in flags:
            return {"message_key": "event.sable.after", "flags_added": [], "items_added": []}
        if not _has_item(user_id, "iron_key"):
            return {"message_key": "event.sable.needs_key", "flags_added": [], "items_added": []}
        _grant_item(user_id, "market_pass", 1)
        _add_flag(user_id, "market_pass_given")
        return {
            "message_key": "event.sable.pass_given",
            "flags_added": ["market_pass_given"],
            "items_added": ["market_pass"],
        }

    if npc_id == "npc_quill":
        if "guild_task_done" in flags and "guild_seal_given" not in flags:
            _grant_item(user_id, "guild_seal", 1)
            _add_flag(user_id, "guild_seal_given")
            return {
                "message_key": "event.quill.task_complete",
                "flags_added": ["guild_seal_given"],
                "items_added": ["guild_seal"],
            }
        if "guild_task_started" not in flags:
            _add_flag(user_id, "guild_task_started")
            return {
                "message_key": "event.quill.task_start",
                "flags_added": ["guild_task_started"],
                "items_added": [],
            }
        return {"message_key": "event.quill.task_wait", "flags_added": [], "items_added": []}

    if npc_id == "npc_elowen":
        if "cross_town_hint" not in flags:
            _add_flag(user_id, "cross_town_hint")
            return {
                "message_key": "event.elowen.cross_town",
                "flags_added": ["cross_town_hint"],
                "items_added": [],
            }
        return {"message_key": "event.elowen.after", "flags_added": [], "items_added": []}

    return None


def _execute_event(user_id, event):
    event_id = event["event_id"]
    flags = []
    items = []

    if event["type"] == "talk_npc":
        npc_id = event["npc_id"]
        special = _special_npc_event(user_id, npc_id)
        if special:
            return special
        return _generic_npc_event(user_id, npc_id)

    if event_id == "read_sign_gate":
        return {"message_key": "event.sign_gate", "flags_added": flags, "items_added": items}

    if event_id == "read_sign_plaza":
        return {"message_key": "event.sign_plaza", "flags_added": flags, "items_added": items}

    if event_id == "enter_hall":
        return {"message_key": "event.enter_hall", "flags_added": flags, "items_added": items}

    if event_id == "enter_guild":
        return {"message_key": "event.enter_guild", "flags_added": flags, "items_added": items}

    current_flags = _get_flags(user_id)

    if event_id == "open_chest_herb":
        if "herb_collected" in current_flags:
            return {"message_key": "event.chest_empty", "flags_added": [], "items_added": []}
        _grant_item(user_id, "herb_bundle", 1)
        _add_flag(user_id, "herb_collected")
        return {
            "message_key": "event.chest_herb_opened",
            "flags_added": ["herb_collected"],
            "items_added": ["herb_bundle"],
        }

    if event_id == "open_chest_archive":
        if "guild_task_started" not in current_flags:
            return {"message_key": "event.archive_locked", "flags_added": [], "items_added": []}
        if "guild_task_done" in current_flags:
            return {"message_key": "event.chest_empty", "flags_added": [], "items_added": []}
        _grant_item(user_id, "sun_ribbon", 1)
        _add_flag(user_id, "guild_task_done")
        return {
            "message_key": "event.archive_found",
            "flags_added": ["guild_task_done"],
            "items_added": ["sun_ribbon"],
        }

    return {"message_key": "event.unknown", "flags_added": [], "items_added": []}


def apply_event(user_id, event_id, payload, client_version):
    snapshot = _town_snapshot(user_id)

    if client_version is not None:
        try:
            client_version = int(client_version)
        except (TypeError, ValueError):
            return 400, {"error_code": "bad_version"}
        if client_version != snapshot["version"]:
            return 409, {"error_code": "stale_client", "snapshot": snapshot}

    events = _event_catalog()
    event = events.get(event_id)
    if not event:
        return 404, {"error_code": "unknown_event"}

    if event_id not in snapshot["allowed_event_ids"]:
        recorded = _load_recorded_event(user_id, event_id)
        if recorded is not None:
            return 200, {"event_id": event_id, "idempotent": True, "event_result": recorded, "snapshot": snapshot}
        return 400, {"error_code": "event_not_allowed", "snapshot": snapshot}

    if not _validate_adjacency(event, payload, snapshot):
        return 400, {"error_code": "invalid_position", "snapshot": snapshot}

    recorded = _load_recorded_event(user_id, event_id)
    if recorded is not None and not event.get("repeatable", False):
        return 200, {"event_id": event_id, "idempotent": True, "event_result": recorded, "snapshot": snapshot}

    result = _execute_event(user_id, event)

    if not event.get("repeatable", False):
        _record_event(user_id, event_id, result)

    _bump_version(user_id)
    fresh = _town_snapshot(user_id)

    return 200, {
        "event_id": event_id,
        "idempotent": False,
        "event_result": result,
        "snapshot": fresh,
    }
