# game_d

Town exploration game prototype with:
- Anonymous persistent player identity
- Grid movement and interaction in the frontend
- Server-validated events and state persistence in the backend

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django + Django REST Framework |
| Frontend | React + Vite |
| Styling | Tailwind CSS + custom CSS |
| Database | MariaDB |

## Project Layout

```text
backend/
  config/
  game/
frontend/
  src/
content/
  ui.json
  dialog/town_dialog.json
  story/town_story.json
scripts/
```

## API Summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/user/me/` | Get or create anonymous user |
| GET | `/api/town/` | Get town snapshot |
| POST | `/api/town/event/` | Trigger a validated town event |

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Tests

```bash
# Backend
cd backend
source venv/bin/activate
python manage.py test game -v2

# Frontend
cd frontend
npx vitest run
```

## Notes

- Game text/content lives under `content/` and is fetched at runtime.
- This repository includes implementation work generated with Codex (GPT-5 based coding model).
