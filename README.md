# Life Tracker

A multi-user daily routine, expense tracker, and next-day planner — built with Django, Redis, HTMX, and Chart.js.

## Features

- **Daily Routines** — checklist with HTMX one-tap complete, weekly heatmap
- **Streak System** — flame counters, badges at 7/14/30/60/100 days
- **Expense Tracker** — colorful Chart.js doughnut, bar, and comparison charts
- **Next-Day Planner** — morning/afternoon/evening blocks, carry-over
- **Draft Autosave** — Redis-backed form drafts (7-day TTL)
- **Multi-User** — separate accounts, isolated data
- **LAN Access** — use from phone/tablet on same WiFi

## Quick Start

### 1. Install Redis (Windows)

Choose one:

- **[Memurai](https://www.memurai.com/)** — Redis-compatible, runs as a Windows service
- **WSL2** — `sudo apt install redis-server && sudo service redis-server start`

### 2. Setup

```bash
cd "F:\code hok\django projects"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
```

### 3. Run (LAN access)

```bash
python manage.py runserver 0.0.0.0:8000
```

Find your PC's IP: `ipconfig` → look for IPv4 Address (e.g. `192.168.0.105`).

Open on any device on the same WiFi: **http://192.168.0.105:8000**

> Allow Windows Firewall access when prompted (Private networks only).

## Use on your phone (like an app)

You only need to type the IP **once**. After that, open it from your home screen.

### Option 1: Add to Home Screen (recommended)

1. On your phone, open `http://192.168.0.102:8000` in the browser (use your PC's IP).
2. **iPhone (Safari):** Share button → **Add to Home Screen** → name it **Life Tracker**
3. **Android (Chrome):** Menu ⋮ → **Add to Home screen** (or tap the **Install** banner)

It will appear as an app icon on your home screen — no address bar, feels like a native app.

Full guide: **http://192.168.0.102:8000/install/** (also in user menu → Install on Phone)

### Option 2: Use a name instead of IP

1. On Windows: **Settings → System → About → Rename this PC** → set to `lifetracker`
2. Restart if prompted
3. On your phone try: **http://lifetracker.local:8000**

Works on many Android phones. iPhone support for `.local` names varies by network.

### Option 3: Bookmark

Save the IP URL as a browser bookmark named **Life Tracker**.


| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (dev key) | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,*` | Hosts for LAN |
| `REDIS_URL` | `redis://127.0.0.1:6379/1` | Redis connection |

## Tech Stack

- Django 6 + django-htmx + django-redis
- SQLite (local) / Redis (sessions, cache, drafts)
- Tailwind CSS + Chart.js (CDN)
- HTMX for interactive UI without a SPA build step
