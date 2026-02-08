import { useCallback, useEffect, useMemo, useState } from 'react'

const GAME_SLUG = import.meta.env.VITE_GAME_SLUG || 'agame'
const URL_PREFIX = GAME_SLUG ? `/${GAME_SLUG}` : ''
const API_BASE = `${URL_PREFIX}/api`
const CONTENT_BASE = `${URL_PREFIX}/content`
const CSRF_COOKIE = GAME_SLUG ? `${GAME_SLUG}_csrf` : 'game_csrf'

const DIRS = {
  north: { x: 0, y: -1 },
  south: { x: 0, y: 1 },
  west: { x: -1, y: 0 },
  east: { x: 1, y: 0 },
}

const KEY_TO_DIR = {
  ArrowUp: 'north',
  w: 'north',
  W: 'north',
  ArrowDown: 'south',
  s: 'south',
  S: 'south',
  ArrowLeft: 'west',
  a: 'west',
  A: 'west',
  ArrowRight: 'east',
  d: 'east',
  D: 'east',
}

function getCsrfToken() {
  const match = document.cookie.match(new RegExp(`${CSRF_COOKIE}=([^;]+)`))
  return match ? match[1] : ''
}

function isPassable(tile) {
  return tile === 'G' || tile === 'P' || tile === 'B'
}

function resolveMessage(table, key) {
  if (!key) {
    return ''
  }
  return table[key] || key
}

function tileClass(tile) {
  if (tile === 'W') return 'tile-wall'
  if (tile === 'P') return 'tile-path'
  if (tile === 'B') return 'tile-bridge'
  return 'tile-grass'
}

function App() {
  const [ui, setUi] = useState(null)
  const [dialogContent, setDialogContent] = useState(null)
  const [town, setTown] = useState(null)
  const [playerPos, setPlayerPos] = useState({ x: 2, y: 2 })
  const [facing, setFacing] = useState('south')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')
  const [dialogMessage, setDialogMessage] = useState('')
  const [interacting, setInteracting] = useState(false)

  const messageTable = dialogContent?.messages || {}
  const npcNameTable = dialogContent?.npcNames || {}
  const itemNameTable = dialogContent?.itemNames || {}
  const itemDescTable = dialogContent?.itemDescriptions || {}
  const flagLabelTable = dialogContent?.flagLabels || {}

  useEffect(() => {
    const fetchJson = async (url, options) => {
      const response = await fetch(url, options)
      if (!response.ok) {
        throw new Error(`request_failed_${response.status}:${url}`)
      }
      return response.json()
    }

    Promise.all([
      fetchJson(`${CONTENT_BASE}/ui.json`),
      fetchJson(`${CONTENT_BASE}/dialog/town_dialog.json`),
      fetchJson(`${API_BASE}/town/`, { credentials: 'include' }),
    ])
      .then(([uiData, dialogData, snapshot]) => {
        setUi(uiData)
        setDialogContent(dialogData)
        setTown(snapshot)
        document.title = uiData.title
        setStatusMessage(uiData.townLoaded || '')
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const eventByPos = useMemo(() => {
    if (!town) {
      return new Map()
    }
    const map = new Map()
    town.events
      .filter((event) => event.state === 'available')
      .forEach((event) => {
        map.set(`${event.pos.x},${event.pos.y}`, event)
      })
    return map
  }, [town])

  const npcByPos = useMemo(() => {
    if (!town) {
      return new Map()
    }
    const map = new Map()
    town.npcs.forEach((npc) => {
      map.set(`${npc.pos.x},${npc.pos.y}`, npc)
    })
    return map
  }, [town])

  const move = useCallback((dir) => {
    if (!town || interacting) {
      return
    }
    const delta = DIRS[dir]
    setFacing(dir)
    setPlayerPos((prev) => {
      const nextX = prev.x + delta.x
      const nextY = prev.y + delta.y
      if (nextX < 0 || nextY < 0 || nextY >= town.height || nextX >= town.width) {
        return prev
      }
      if (!isPassable(town.tiles[nextY][nextX])) {
        return prev
      }
      if (npcByPos.has(`${nextX},${nextY}`)) {
        return prev
      }
      return { x: nextX, y: nextY }
    })
  }, [interacting, npcByPos, town])

  const interact = useCallback(async () => {
    if (!town || !ui || interacting) {
      return
    }

    const delta = DIRS[facing]
    const target = { x: playerPos.x + delta.x, y: playerPos.y + delta.y }
    const event = eventByPos.get(`${target.x},${target.y}`)

    if (!event) {
      setStatusMessage(ui.statusNoTarget || '')
      return
    }

    setInteracting(true)
    setStatusMessage(ui.statusInteracting || '')

    try {
      const response = await fetch(`${API_BASE}/town/event/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
          event_id: event.event_id,
          version: town.version,
          payload: {
            player_position: playerPos,
            target_position: target,
          },
        }),
      })

      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        if (data.error_code === 'stale_client' && data.snapshot) {
          setTown(data.snapshot)
          setStatusMessage(ui.eventStale || '')
          return
        }

        const codeMap = {
          invalid_position: ui.eventBadPosition,
          event_not_allowed: ui.eventDenied,
          unknown_event: ui.eventUnknown,
          no_session: ui.eventNoSession,
        }
        setStatusMessage(codeMap[data.error_code] || `${ui.errorPrefix || ''} ${data.error_code || ''}`)
        return
      }

      if (data.snapshot) {
        setTown(data.snapshot)
      }

      const text = resolveMessage(messageTable, data.event_result?.message_key)
      setDialogMessage(text)
      setStatusMessage(text)
    } catch (err) {
      setStatusMessage(`${ui.errorPrefix || ''} ${err.message}`)
    } finally {
      setInteracting(false)
    }
  }, [eventByPos, facing, interacting, messageTable, playerPos, town, ui])

  useEffect(() => {
    const onKeyDown = (event) => {
      const key = event.key
      if (key === 'e' || key === 'E' || key === ' ') {
        event.preventDefault()
        interact()
        return
      }
      const dir = KEY_TO_DIR[key]
      if (dir) {
        event.preventDefault()
        move(dir)
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [interact, move])

  if (loading) {
    return <div className="screen-root loading-panel">{ui?.loading || ''}</div>
  }

  if (error) {
    return <div className="screen-root error-panel">{ui?.errorPrefix || ''} {error}</div>
  }

  const facingLabelKey = {
    north: 'facingNorth',
    south: 'facingSouth',
    west: 'facingWest',
    east: 'facingEast',
  }[facing]

  const flags = town?.player_state?.flags || []
  const items = town?.player_state?.items || []

  return (
    <div className="screen-root">
      <div className="backdrop" />
      <main className="layout-grid">
        <section className="panel panel-map">
          <h1>{ui.title}</h1>
          <div
            className="town-grid"
            style={{ gridTemplateColumns: `repeat(${town.width}, minmax(0, 1fr))` }}
          >
            {town.tiles.flatMap((row, y) => row.split('').map((tile, x) => {
              const key = `${x},${y}`
              const npc = npcByPos.get(key)
              const event = eventByPos.get(key)
              const isPlayer = playerPos.x === x && playerPos.y === y

              return (
                <div key={key} className={`tile ${tileClass(tile)}`}>
                  {event && !npc && !isPlayer && <span className="glyph glyph-event">*</span>}
                  {npc && !isPlayer && <span className="glyph glyph-npc">N</span>}
                  {isPlayer && <span className="glyph glyph-player">@</span>}
                </div>
              )
            }))}
          </div>
          <p className="status-line">{statusMessage}</p>
          <div className="legend-row">
            <span>@ {ui.legendPlayer}</span>
            <span>N {ui.legendNpc}</span>
            <span>* {ui.legendEvent}</span>
          </div>
        </section>

        <section className="panel panel-side">
          <div className="stack">
            <h2>{ui.controlsTitle}</h2>
            <p>{ui.controlsMove}</p>
            <p>{ui.controlsTalk}</p>
            <p>{ui.controlsHint}</p>
          </div>

          <div className="stack">
            <h2>{ui.statusTitle}</h2>
            <p>{ui.statusCoords}: {playerPos.x},{playerPos.y}</p>
            <p>{ui.statusFacing}: {ui[facingLabelKey]}</p>
            <p>{ui.statusVersion}: {town.version}</p>
            <p>{ui.statusTownId}: {town.town_id}</p>
          </div>

          <div className="stack">
            <h2>{ui.dialogTitle}</h2>
            <p>{dialogMessage}</p>
          </div>

          <div className="stack">
            <h2>{ui.inventoryTitle}</h2>
            {items.length === 0 && <p>{ui.emptyInventory}</p>}
            {items.map((item) => (
              <p key={item.item_id}>
                {itemNameTable[item.name_key] || item.name_key} x{item.qty}<br />
                <span className="subtle">{itemDescTable[item.description_key] || item.description_key}</span>
              </p>
            ))}
          </div>

          <div className="stack">
            <h2>{ui.flagsTitle}</h2>
            {flags.length === 0 && <p>{ui.emptyFlags}</p>}
            {flags.map((flag) => (
              <p key={flag}>{flagLabelTable[flag] || flag}</p>
            ))}
          </div>

          {town.version >= (ui.codexFootnoteThresholdVersion || Number.MAX_SAFE_INTEGER) && (
            <p className="codex-footnote">{ui.codexFootnote}</p>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
