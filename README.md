# Fuma Gacha Bot

Fuma is a Discord gacha bot for K‑pop communities with a custom card system, economy, and an accompanying web panel for management and monitoring. Users collect cards, trade or gift them, and participate in events; staff can create cards, run events, and moderate usage.

This repository contains both:
- The Discord bot (Hikari + Lightbulb + Miru)
- A FastAPI-based web panel (Uvicorn + Starlette + Jinja2 + SQLite)


## Feature Overview

### Cards & Gacha
- Pull cards with rarities (1–5) and pullability flags.
- Card types: Standard, Event, Limited. Limited cards typically drop only during limited events.
- Inventory management: view your collection and individual card details.
- Gift/trade cards between users.
- Global card registry with unique identifiers and metadata (name, description, rarity, tier, group, pullable).

### Economy
- Two currencies: Fuma Coins (common) and Nicho Points (rare, used for limited cards).
- Earn through gameplay commands (e.g., gym/poke battles and other cooldown-gated actions).
- Balance lookup and peer-to-peer payments.

### Shops & Market
- Pokéshop (in-bot shop):
  - Browse and buy packs (variety/random) with configurable filters and amounts.
  - Staff can add/remove items from shop stock.
- Nicho Market (player marketplace):
  - Browse, buy, and sell cards for Nicho Points.
  - Cross-server friendly seller display (stores display names with offers).

### Events
- Standard events: definable and schedulable; attach event-specific cards.
- Limited events: separate schedule and card associations for limited drops.
- Background notification tasks for both standard and limited events.

### Staff / Administration
- Centralized control model: a single group controls an instance of the bot.
- Admins and staff are determined by hard-coded user IDs and role IDs in the bot config.
- Commands to create/remove/spawn cards and manage events (create, schedule, associate cards).
- Ban/unban users from bot usage.
- Bot logging: set channel for bot activity logs and internal diagnostics.

### Utilities & Quality of Life
- Slash command help and summary.
- Cooldown handling for applicable commands.
- Error handling with user-facing feedback and internal logging.
- Bug reporting flow (user-submitted reports with reproduction details, severity, optional traceback capture).
- Command enable/disable toggles stored in the database.

### Web Panel (FastAPI)
- Modular web application with dynamic module loading for routes and static assets.
- Modules included:
  - Home dashboard
  - Login/Register (token-based sessions stored in SQLite)
  - Cards (list and detail views; management helpers)
  - Commands (view bot commands and their status)
  - Errors (view, resolve, ignore bug reports)
  - Log Viewer (browse and search logs)
- Custom 401 redirect and 404 page, favicon serving.


## Tech Stack
- Discord: hikari, hikari-lightbulb (slash commands), hikari-miru (components)
- Web: FastAPI, Starlette, Jinja2, Uvicorn
- Data: SQLite with an auto-migration/modernization routine on startup
- Logging: daily rotating file per date in the logs/ directory


## How It Works (High Level)
- On startup, the bot modernizes the SQLite schema to the current shape.
- All cogs (extensions) are auto-loaded for cards, economy, shops, market, staff, events, and misc utilities.
- The FastAPI web panel is started alongside the Discord bot (default on port 8010).


## Quick Start
1. Requirements
   - Python 3.12+
   - pip install -r requirements.txt
2. Set environment variables
   - BOT_TOKEN: your Discord bot token (required; the bot will refuse to start without it)
   - DEBUG: optional, set to true to bind the web panel to 127.0.0.1 instead of 0.0.0.0
3. Run
   - python bot.py
4. Access the web panel
   - http://localhost:8010/

Notes
- Logs are written to logs/YYYY-MM-DD.log.
- Database file defaults to botapp.sqlite in the project root.


## Configuration & Access Control
- Centralized bot: only one group administers an instance.
- Admins are defined by user IDs and role IDs in bot.py (botapp.d['admin_ids'] and botapp.d['admin_roles']).
- Maintainer ID is set in bot.py for privileged internal tasks.
- Event channel and other runtime config values are stored in botapp.d and/or the database.


## Project Structure (Highlights)
- bot.py: entry point; starts both the Discord bot and the web panel.
- cogs/: feature groups (cards, economy, shops, staff/tools, events, errors, help).
- library/: bot wiring, decorators, database and DB modules, command toggles.
- webpanel/: FastAPI app, modules, templates, static assets, auth helper.
- logs/: daily log files.


## Credits & Community
Fumabot is built for a gacha + K‑pop community. For support and feedback, see the in-bot /help command for the community server link.