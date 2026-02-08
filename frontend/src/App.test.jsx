import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'

const MOCK_UI = {
  title: 'B Game: Town of Threads',
  loading: 'Loading town...',
  errorPrefix: 'Error:',
  townLoaded: 'Town ready.',
  controlsTitle: 'Controls',
  controlsMove: 'Move: WASD or Arrow Keys',
  controlsTalk: 'Talk/Use: E or Space',
  controlsHint: 'Walk up to a person or marker, then press talk.',
  legendPlayer: 'You',
  legendNpc: 'Citizen',
  legendEvent: 'Interactable',
  statusTitle: 'Status',
  statusCoords: 'Position',
  statusFacing: 'Facing',
  statusVersion: 'Town Version',
  statusTownId: 'Town',
  statusNoTarget: 'No nearby interaction target.',
  statusInteracting: 'Interacting...',
  facingNorth: 'North',
  facingSouth: 'South',
  facingWest: 'West',
  facingEast: 'East',
  dialogTitle: 'Dialog',
  inventoryTitle: 'Inventory',
  flagsTitle: 'Quest Flags',
  emptyInventory: 'No items yet.',
  emptyFlags: 'No flags yet.',
  eventDenied: 'That action is not allowed right now.',
  eventStale: 'Your town version was stale. Snapshot refreshed.',
  eventBadPosition: 'Move next to the target and try again.',
  eventUnknown: 'Unknown interaction.',
  eventNoSession: 'Session missing. Reload the page.',
  codexFootnoteThresholdVersion: 14,
  codexFootnote: 'Deep in the town archives: built with Codex (GPT-5 based coding model).',
}

const MOCK_DIALOG = {
  npcNames: {},
  messages: {
    'event.sign_gate': 'Gate District message.',
  },
  itemNames: {},
  itemDescriptions: {},
  flagLabels: {},
}

const BASE_SNAPSHOT = {
  town_id: 'town-000001',
  seed: 123,
  width: 8,
  height: 6,
  tiles: [
    'WWWWWWWW',
    'WGGGGGGW',
    'WGGPGGGW',
    'WGGGGGGW',
    'WGGGGGGW',
    'WWWWWWWW',
  ],
  npcs: [{ npc_id: 'npc_lyra', name_key: 'npc.npc_lyra', pos: { x: 5, y: 2 }, event_ids: ['talk_npc_lyra'] }],
  events: [{ event_id: 'read_sign_gate', type: 'read_sign', state: 'available', pos: { x: 4, y: 2 } }],
  allowed_event_ids: ['read_sign_gate'],
  version: 1,
  player_state: {
    flags: [],
    items: [],
  },
}

function setupFetchMock() {
  global.fetch = vi.fn((url, options) => {
    if (url === '/agame/content/ui.json') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_UI) })
    }
    if (url === '/agame/content/dialog/town_dialog.json') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(MOCK_DIALOG) })
    }
    if (url === '/agame/api/town/') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(BASE_SNAPSHOT) })
    }
    if (url === '/agame/api/town/event/' && options?.method === 'POST') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          event_id: 'read_sign_gate',
          idempotent: false,
          event_result: { message_key: 'event.sign_gate', flags_added: [], items_added: [] },
          snapshot: { ...BASE_SNAPSHOT, version: 2 },
        }),
      })
    }

    return Promise.reject(new Error(`unmocked_${url}`))
  })
}

async function renderLoadedApp() {
  render(<App />)
  await waitFor(() => {
    expect(screen.getByText('B Game: Town of Threads')).toBeInTheDocument()
  })
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('Town App', () => {
  beforeEach(() => {
    setupFetchMock()
  })

  it('loads and renders town UI', async () => {
    await renderLoadedApp()
    expect(screen.getByText('Controls')).toBeInTheDocument()
    expect(screen.getByText('Town ready.')).toBeInTheDocument()
  })

  it('movement key does not trigger network calls', async () => {
    await renderLoadedApp()
    const before = global.fetch.mock.calls.length
    fireEvent.keyDown(window, { key: 'd' })
    fireEvent.keyDown(window, { key: 's' })
    const after = global.fetch.mock.calls.length
    expect(after).toBe(before)
  })

  it('talk key posts event endpoint', async () => {
    await renderLoadedApp()

    fireEvent.keyDown(window, { key: 'd' })
    fireEvent.keyDown(window, { key: 'E' })

    await waitFor(() => {
      const postCall = global.fetch.mock.calls.find(
        ([url, options]) => url === '/agame/api/town/event/' && options?.method === 'POST'
      )
      expect(postCall).toBeTruthy()
      expect(screen.getAllByText('Gate District message.').length).toBeGreaterThan(0)
    })
  })

  it('shows deep codex footnote only at threshold', async () => {
    await renderLoadedApp()
    expect(screen.queryByText(MOCK_UI.codexFootnote)).not.toBeInTheDocument()

    fireEvent.keyDown(window, { key: 'd' })
    fireEvent.keyDown(window, { key: 'E' })
    await waitFor(() => {
      expect(screen.queryByText(MOCK_UI.codexFootnote)).not.toBeInTheDocument()
    })
  })
})
