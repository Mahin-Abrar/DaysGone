# AGENTS.md — Life Tracker

> Guide for AI agents working on this codebase. Read this before making changes.

## What this app is

**Life Tracker** is a multi-user personal dashboard for:

- **Daily routines** (habits with schedules, HTMX complete toggle, weekly liquid progress bars)
- **Expense tracking** (categories, Chart.js charts, monthly filters)
- **Next-day planner** (morning/afternoon/evening blocks, carry-over)
- **Streak rewards** (badges at 7/14/30/60/100 days, Redis-cached streak reads)
- **Draft autosave** (Redis-backed form drafts for expenses & planner)

Deployed for **local WiFi LAN access** (`0.0.0.0:8000`) with **PWA** support (install to home screen). Not intended for public internet exposure.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 6.x, Python 3.11+ |
| Database | SQLite (`db.sqlite3`) |
| Cache / Sessions / Drafts | Redis via `django-redis` (`IGNORE_EXCEPTIONS: True` — app runs without Redis but drafts/sessions degrade) |
| UI | Django templates + Tailwind CDN + HTMX + custom CSS (`static/css/app.css`) |
| Charts | Chart.js 4 (CDN) |
| Auth | Django built-in `User` model |
| Config | `python-dotenv` (`.env`) |

**No separate frontend build** (no npm/Vite). All JS is vanilla in `static/js/`.

---

## Project layout

```
django projects/
├── manage.py
├── requirements.txt
├── .env                          # SECRET_KEY, DEBUG, ALLOWED_HOSTS, REDIS_URL
├── run.bat                       # Windows launcher (venv + runserver 0.0.0.0:8000)
├── README.md
├── AGENTS.md                     # This file
│
├── config/                       # Django project package
│   ├── settings.py               # Main settings, Redis, apps, context processors
│   ├── urls.py                   # Root URL routing
│   ├── views.py                  # Dashboard view only
│   ├── pwa_views.py              # Service worker + /install/ guide page
│   ├── admin.py                  # Registers all models in admin
│   ├── apps.py                   # ConfigConfig (enables management commands)
│   └── management/commands/
│       └── seed_data.py          # Seeds default expense categories + badges
│
├── accounts/                     # Auth + user profile
├── routines/                     # Daily habits
├── expenses/                     # Expense tracker
├── planner/                      # Next-day planner
├── rewards/                      # Streaks + badges (logic lives here)
├── drafts/                       # Redis draft save/load API (no models)
│
├── templates/
│   ├── base.html                 # Nav, user menu, PWA meta, mobile bottom nav
│   ├── dashboard.html            # Home page (/)
│   ├── accounts/                 # login, register, profile
│   ├── routines/                 # list, form, partials/routine_card.html
│   ├── expenses/                 # list (charts), form
│   ├── planner/                  # list, form, partials/item.html
│   └── rewards/                  # list
│
└── static/
    ├── css/app.css               # All custom styles, animations, liquid bars, PWA
    ├── js/app.js                 # Theme, user menu, page transitions, PWA, avatar picker
    ├── js/charts.js              # Chart.js helpers (doughnut, bar, line)
    ├── js/drafts.js              # Autosave for .draft-form elements
    ├── sw.js                     # Service worker (light precache)
    ├── manifest.webmanifest      # PWA manifest
    └── icons/                    # icon-192.png, icon-512.png
```

---

## URL map

| Path | App | View | Notes |
|---|---|---|---|
| `/` | config | `dashboard` | Login required; unified home |
| `/admin/` | django | admin | All models registered |
| `/sw.js` | config | `service_worker` | PWA service worker |
| `/install/` | config | `install_guide` | Phone install instructions |
| `/accounts/login/` | accounts | `CustomLoginView` | |
| `/accounts/register/` | accounts | `register` | Auto-login after register |
| `/accounts/logout/` | accounts | `CustomLogoutView` | |
| `/accounts/profile/` | accounts | `profile` | Avatar, color, timezone, currency |
| `/routines/` | routines | `routine_list` | Today checklist + weekly heatmap |
| `/routines/new/` | routines | `routine_create` | Icon emoji picker |
| `/routines/<pk>/edit/` | routines | `routine_edit` | |
| `/routines/<pk>/complete/` | routines | `routine_complete` | POST, HTMX partial |
| `/routines/<pk>/uncomplete/` | routines | `routine_uncomplete` | POST, HTMX partial |
| `/routines/<pk>/delete/` | routines | `routine_delete` | POST |
| `/expenses/` | expenses | `expense_list` | Charts + recent list |
| `/expenses/new/` | expenses | `expense_create` | Draft autosave |
| `/expenses/<pk>/delete/` | expenses | `expense_delete` | POST |
| `/planner/` | planner | `planner_view` | Default: tomorrow's date |
| `/planner/new/` | planner | `planner_create` | Draft autosave |
| `/planner/<pk>/toggle/` | planner | `planner_toggle` | POST, HTMX |
| `/planner/<pk>/delete/` | planner | `planner_delete` | POST, HTMX |
| `/planner/<pk>/move/<dir>/` | planner | `planner_move` | up/down reorder |
| `/planner/carryover/` | planner | `planner_carryover` | POST — copy unfinished today → tomorrow |
| `/rewards/` | rewards | `rewards_view` | Streaks + badge shelf |
| `/drafts/save/` | drafts | `save_draft_view` | POST JSON |
| `/drafts/load/` | drafts | `load_draft_view` | GET JSON |
| `/drafts/delete/` | drafts | `delete_draft_view` | POST JSON |

---

## Django apps — models & responsibilities

### `accounts`

| Model | Fields | Notes |
|---|---|---|
| `Profile` | `user` (1:1), `avatar` (emoji), `avatar_color`, `timezone`, `currency` | Auto-created via `signals.py` on User save |

- `accounts/avatars.py` — 20 emoji choices for profile avatar
- `accounts/context_processors.py` — injects `user_profile` into all templates
- Profile form uses emoji grid + color swatches (JS in `app.js` → `initAvatarPicker`)

### `routines`

| Model | Fields | Notes |
|---|---|---|
| `Routine` | `user`, `title`, `color`, `icon`, `schedule`, `custom_days`, `target_time`, `is_active` | `is_due_on(date)` method for schedule logic |
| `RoutineLog` | `user`, `routine`, `date`, `completed_at`, `note` | Unique per user/routine/date |

- `routines/icons.py` — 30 emoji icons for routine form picker
- Schedule choices: `daily`, `weekdays`, `weekends`, `custom` (comma weekday nums 0=Mon)
- HTMX: completing a routine swaps `partials/routine_card.html` in place
- Weekly heatmap built in `routine_list` view; liquid CSS animation in template + JS

### `expenses`

| Model | Fields | Notes |
|---|---|---|
| `Category` | `user` (nullable), `name`, `color`, `icon`, `is_default` | Defaults seeded globally (`user=None`) |
| `Expense` | `user`, `category`, `amount`, `date`, `note`, `payment_method` | |

- Categories query: `Q(user=user) | Q(is_default=True, user__isnull=True)`
- Charts rendered client-side in `expenses/list.html` via `charts.js`

### `planner`

| Model | Fields | Notes |
|---|---|---|
| `PlannerItem` | `user`, `target_date`, `title`, `priority`, `time_block`, `is_done`, `order` | |

- Default view date: **tomorrow** (`_tomorrow()` helper)
- Time blocks: `morning`, `afternoon`, `evening`, `anytime`
- Priority: `high`, `medium`, `low`

### `rewards`

| Model | Fields | Notes |
|---|---|---|
| `Badge` | `name`, `description`, `icon`, `milestone_days`, `color` | Seeded at 7/14/30/60/100 days |
| `Streak` | `user`, `routine`, `current_streak`, `longest_streak`, `last_completed_date` | Unique user+routine |
| `UserBadge` | `user`, `badge`, `routine`, `earned_at` | Unique user+badge+routine |

**Key business logic** (in `rewards/models.py`):

- `update_streak(user, routine, completed_date)` — called on routine complete; awards badges; invalidates Redis cache
- `check_missed_streaks(user)` — resets streak to 0 if scheduled days were missed; called on routines list load
- `Streak.get_cached(user, routine)` — Redis key `streak:{user_id}:{routine_id}`, 5-min TTL

### `drafts`

No models. Redis-only via `drafts/utils.py`:

- Key format: `draft:{user_id}:{form_type}:{object_id}`
- TTL: 7 days (`settings.DRAFT_TTL`)
- Used by: expense form, planner form (`drafts.js` autosaves on input with 2s debounce)

---

## Frontend architecture

### Base template (`templates/base.html`)

- Sticky top nav (desktop links) + fixed bottom nav (mobile, ≤768px)
- User avatar dropdown (profile, install guide, logout)
- Theme toggle button (visible on **all** screen sizes) + dark mode in mobile dropdown
- `#page-content` wrapper for page enter/exit animations
- Nav links use class `internal-nav` for smooth transitions (`app.js` → `initPageTransitions`)

### CSS (`static/css/app.css`)

Single source of truth for custom styles. Tailwind CDN handles utilities; do **not** rely on `@apply` in templates (only works in CSS file if Tailwind processes it — currently CDN mode, so custom classes are plain CSS).

Key classes:
- `.card`, `.btn-primary`, `.btn-secondary`, `.stat-card`
- `.animate-item` — staggered entrance animations (`--delay` CSS var)
- `.liquid-bar-container`, `.liquid-fill` — weekly progress liquid effect
- `.icon-picker-*` — routine emoji picker
- `.user-dropdown`, `.mobile-nav` — navigation chrome

### JavaScript

| File | Purpose |
|---|---|
| `app.js` | Theme, user menu, page transitions, PWA install banner, avatar picker |
| `charts.js` | `initDoughnutChart`, `initBarChart`, `initLineChart` |
| `drafts.js` | Autosave for forms with `.draft-form` + `data-form-type` |

### HTMX usage

- `request.htmx` checked in views to return partials vs redirects
- Routine complete/uncomplete → `routines/partials/routine_card.html`
- Planner toggle/delete → `planner/partials/item.html`
- `django_htmx.middleware.HtmxMiddleware` enabled in settings

---

## Data flows (critical paths)

### Routine complete → streak update

```
POST /routines/<pk>/complete/
  → RoutineLog created (if new)
  → update_streak() in rewards/models.py
  → Streak saved, UserBadge maybe created
  → Streak.invalidate_cache()
  → HTMX returns updated routine_card.html
```

### Expense draft → save

```
User types in expense form
  → drafts.js POST /drafts/save/ (debounced 2s)
  → Redis: draft:{user_id}:expense:new
On form submit → Expense saved → delete_draft()
```

### Dashboard data sources

`config/views.py` aggregates from all apps:
- Routine progress from `Routine` + `RoutineLog`
- Streaks from `Streak`
- Expenses from `Expense` (current month)
- Tomorrow preview from `PlannerItem`
- Badges from `UserBadge`

---

## Redis usage summary

| Use | Key pattern | TTL |
|---|---|---|
| Sessions | Django session keys (prefixed `lifetracker`) | Session |
| Streak cache | `streak:{user_id}:{routine_id}` | 5 min |
| Drafts | `draft:{user_id}:{form_type}:{object_id}` | 7 days |

Redis is optional at runtime (`IGNORE_EXCEPTIONS: True`). Install Memurai (Windows) or WSL Redis for full functionality.

---

## Environment & commands

```bash
# Setup
python -m venv venv
.\venv\Scripts\activate          # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data       # Required: categories + badges
python manage.py createsuperuser

# Run (LAN)
python manage.py runserver 0.0.0.0:8000
# Or: .\run.bat
```

### `.env` variables

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | dev key | Django secret |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,*` | LAN access |
| `REDIS_URL` | `redis://127.0.0.1:6379/1` | Redis connection |

---

## Conventions for agents

### Do

- Keep changes **minimal and scoped** — match existing patterns in each app
- Use `INPUT_CLASS` constant in forms (module-level, not class attribute — Python scoping issue)
- Filter all user data by `request.user` in views
- Use `@login_required` on all app views (except auth)
- Put shared template components in `partials/` subfolders
- Add new static JS to `static/js/`, styles to `static/css/app.css`
- Use `internal-nav` class on new nav links for page transitions

### Don't

- Don't add npm/React/Vue — project is server-rendered by design
- Don't edit the plan file in `.cursor/plans/` unless asked
- Don't expose to internet without HTTPS + proper `ALLOWED_HOSTS` + `DEBUG=False`
- Don't use `input_class` as a class attribute inside `Meta.widgets` (causes `NameError`)
- Don't commit `.env`, `db.sqlite3`, or `venv/`

### Adding a new feature

1. Model in appropriate app → `makemigrations` → `migrate`
2. Form in `forms.py`, view in `views.py`, urls in `urls.py`
3. Template in `templates/<app>/`
4. Register model in `config/admin.py` if needed
5. Add nav link in `templates/base.html` (desktop + mobile) with `internal-nav`
6. If user-specific: always filter by `request.user`

---

## PWA / mobile

- `static/manifest.webmanifest` — app name "Life Tracker", standalone display
- `static/sw.js` — light service worker; served at `/sw.js`
- `/install/` — HTML guide for Add to Home Screen
- Install banner in `base.html`, logic in `app.js` → `initPWA()`
- Access from phone: `http://<PC_LAN_IP>:8000` (e.g. `192.168.0.102:8000`)

---

## What is implemented (as of last update)

- [x] Multi-user auth (register, login, profile)
- [x] Routines with schedules, HTMX complete, weekly liquid heatmap
- [x] Routine emoji icon picker (30 icons)
- [x] Streak system + badges + Redis cache
- [x] Expenses with Chart.js (doughnut, bar, month comparison)
- [x] Planner with time blocks, reorder, carry-over
- [x] Draft autosave (expenses, planner)
- [x] Dashboard with animated sections
- [x] Dark/light mode (desktop + mobile)
- [x] User avatar emoji + color picker
- [x] Page transition animations
- [x] PWA manifest + install guide
- [x] LAN deployment (`0.0.0.0:8000`)

## Not implemented / future ideas

- [ ] Drag-to-reorder planner items (v1 uses up/down links)
- [ ] PostgreSQL swap (SQLite is fine for LAN)
- [ ] Docker Compose (Django + Redis + Gunicorn)
- [ ] Routine note drafts
- [ ] Email notifications
- [ ] Custom domain via mDNS (`lifetracker.local`) — documented in README only
- [ ] Automated tests (0 tests currently)
- [ ] Rename app from "Life Tracker" to chosen brand name

---

## Key files quick reference

| Task | Look here |
|---|---|
| Change global settings | `config/settings.py` |
| Add URL route | `config/urls.py` + app `urls.py` |
| Dashboard logic | `config/views.py` |
| Streak/badge logic | `rewards/models.py` |
| Routine schedule logic | `routines/models.py` → `is_due_on()` |
| Nav / layout | `templates/base.html` |
| Animations / liquid bars | `static/css/app.css` |
| Page transitions / theme | `static/js/app.js` |
| Seed data | `python manage.py seed_data` |
| PWA | `static/manifest.webmanifest`, `config/pwa_views.py` |

---

## Demo credentials

- Username: `demo`
- Password: `demo1234`

(Created manually during development; may or may not exist in fresh installs.)
