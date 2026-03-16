# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ha-addons** is a repository containing Home Assistant addons:

| Addon | Version | Description |
|-------|---------|-------------|
| **Lyric Scroll** | v0.5.16 | Synchronized, scrolling lyrics for Music Assistant |
| **Ground Control** | v0.1.5 | Task and project management UI |

## Agent Identity

You are **GCA (Ground Control Agent)**. You build and maintain the HA addons in this repo.

Your counterpart is **Major Tom**, who operates inside Home Assistant (`/config/` in ha-config repo). You coordinate with Major Tom via MQTT messaging (see Agent Sync System below).

---

## Agent Sync System

GCA and Major Tom communicate via MQTT with automatic message delivery.

### How It Works

1. **MQTT Transport**: Messages are JSON payloads on retained topics
2. **Hook Automation**: A `UserPromptSubmit` hook auto-receives messages at each turn
3. **Messages appear in context**: New messages from Major Tom show as `[MQTT SYNC]` system reminders

### Quick Commands

```bash
# Check for new messages (auto-runs via hook)
cd .claude/sync && source .venv/bin/activate && python mqtt-sync.py receive

# Send messages from outbox
python mqtt-sync.py send

# Test connection
python mqtt-sync.py status
```

### Writing Messages

Create `.md` files in `.claude/sync/outbox/` with this format:

```markdown
---
from: gca
to: major-tom
date: 2026-03-15
subject: Brief subject
type: update
priority: normal
response: none
---

# Subject

Content here.
```

Then run `python mqtt-sync.py send` to publish.

### Message Types
- `handoff` - Passing work or context
- `question` - Requesting information
- `update` - Status update
- `ack` - Acknowledging receipt

### Response Field
- `required` - You're blocked, need answer
- `optional` - Feedback welcome, will proceed if none
- `none` - Informational only (default)

---

## Lyric Scroll Addon

Lyric Scroll is a Home Assistant addon that displays synchronized, scrolling lyrics for music playing via Music Assistant. It supports casting to Google Cast devices (Chromecast, Nest Hub, etc.).

## Terminology & Glossary

| Term | Meaning |
|------|---------|
| **FB** / **Fallback Screen** | The screen shown when no song is playing (clock + recently played on cast-receiver) |
| **LD** | Lyric Display - the Chromecast/display device we cast lyrics to |
| **laptop_browser** | User's laptop browser, typically at `https://lyric-scroll.mattmariani.com` |
| **HA** | Home Assistant dashboard |
| **addon settings** | The in-page slide-out settings modal within the web UI |
| **config screen** | The addon Configuration tab in HA (between Info and Logs tabs) |
| **addon** / **app** | Synonymous - HA renamed "addons" to "apps" but we use "addon" |

**Status Format**: "the addon shows `<content>` on `<device>`"
- Example: "the addon shows FB on LD" = fallback screen on lyric display
- Example: "the addon shows lyrics on laptop_browser" = lyrics in browser

## Casting Architecture

The casting flow uses a **shell/container app** running on piUSBcam:

1. **piUSBcam** (192.168.4.158:9123) hosts `cast-receiver` (separate repo: `loydmilligan/cast-receiver`)
2. **Cast App ID**: `76719249` (registered to piUSBcam receiver URL)
3. **Namespace**: `urn:x-cast:com.casttest.custom`
4. **Flow**:
   - Addon detects song → sends `loadUrl` via chromecast_caster.py
   - piUSBcam receiver loads lyrics URL in iframe
   - Song stops → sends `clearUrl` → receiver shows FB (clock)

**URLs**:
- Receiver: `http://192.168.4.158:9123/receiver.html` (HTTP OK for receiver)
- Lyrics: `https://lyric-scroll.mattmariani.com` (HTTPS required for iframe content)

## Architecture

- **Backend**: Python 3 with aiohttp (async web framework)
- **Frontend**: Vanilla JavaScript with WebSocket for real-time sync
- **Deployment**: Home Assistant addon (containerized)
- **Integration**: Home Assistant WebSocket API, Music Assistant

### Key Files

| File | Purpose |
|------|---------|
| `lyric-scroll/app/main.py` | Main app, API routes, WebSocket server |
| `lyric-scroll/app/ha_client.py` | Home Assistant WebSocket client |
| `lyric-scroll/app/ma_client.py` | Music Assistant integration |
| `lyric-scroll/app/lyrics_fetcher.py` | Lyrics fetching (LRCLIB) |
| `lyric-scroll/frontend/js/app.js` | Frontend logic |
| `lyric-scroll/frontend/index.html` | Frontend HTML |
| `lyric-scroll/config.yaml` | HA addon configuration |

## Testing & Deploying

**CRITICAL: Always follow these steps after making changes:**

1. **Update version in ALL locations:**
   - `lyric-scroll/config.yaml` - `version: "X.Y.Z"`
   - `lyric-scroll/frontend/index.html` - `<span id="version">vX.Y.Z</span>`

2. **Verify Python syntax:**
   ```bash
   python3 -m py_compile lyric-scroll/app/main.py
   python3 -m py_compile lyric-scroll/app/ha_client.py
   ```

3. **Commit and push ALL changes:**
   ```bash
   git add -A
   git commit -m "Description (vX.Y.Z)"
   git push
   ```

4. **User refreshes addon in Home Assistant** to pull the new version

**DO NOT** wait to be asked - always update version, commit, and push after completing any code changes.

## Build Commands

No build step required. Python and frontend files are served directly.

## Settings Storage

- **HA addon options**: `/data/options.json`
- **App settings**: `/data/settings.json`
- **Lyrics cache**: `/data/cache/`

## API Endpoints

- `GET /` - Frontend
- `GET /ws` - WebSocket for live sync
- `GET /api/settings` - Get settings
- `POST /api/settings` - Update settings
- `GET /api/ma/players` - List MA players
- `GET /api/ma/displays` - List Cast displays
- `POST /api/ma/queue` - Queue tracks

## Log Access (for Claude)

Logs and LRC files are synced via PowerShell watcher to local folder:
- **Source**: NAS share `\\192.168.6.31\shared\lrc` (addon exports here)
- **Destination**: `C:\Users\mmariani\Music\lrc\`
- **Path in WSL**: `/mnt/c/Users/mmariani/Music/lrc/`
- **Logs**: `/mnt/c/Users/mmariani/Music/lrc/logs/lyric_scroll.log`

**Sync Script**: `C:\Users\mmariani\scripts\sync-lrc.ps1`
- Run in PowerShell: `.\sync-lrc.ps1`
- LRC files: synced every 2s (real-time for lyrics)
- Log files: synced every 30s (less bandwidth for large logs)

**Quick log access**:
```bash
python3 tests/ha_control.py logs           # Last 50 lines
python3 tests/ha_control.py logs -n 100    # Last 100 lines
python3 tests/ha_control.py logs -f        # Follow (tail -f)
```

## Roadmap

### Sync Improvements (Priority)
- [ ] **Autosync toggle** - Bring back from v0.6.2 with fixes (caused issues before)
- [ ] **Jump buttons** - Add +/- buttons for precise timeline adjustments (small: ±1s, large: ±5s)
- [ ] **Audio timeline indicator** - Visual indicator showing audio's current position alongside lyric scrubber
- [ ] **Sync hint markers** - Visual cues in LRC files for sync points

### Settings Cleanup
- [ ] Simplify settings - remove redundant options
- [ ] Move casting config to addon config tab
- [ ] Single player selection (multi-player mapping later)

### Testing Apparatus
- [x] Export addon logs to samba share for Claude access
- [x] Script to trigger addon restart via HA API
- [x] Script to start playback on test player
- [x] Sync verification test (screenshots + position comparison)

**Test Scripts** (in `tests/` folder):

| Script | Purpose |
|--------|---------|
| `ha_control.py` | Control HA/addon: restart, play, pause, status, position, logs |
| `quick_sync_check.py` | API-only sync monitoring, detects jumps/stutters |
| `sync_test.py` | Full test with screenshots (requires playwright) |

**Usage:**
```bash
# View addon logs (synced via PowerShell)
python3 tests/ha_control.py logs          # Last 50 lines
python3 tests/ha_control.py logs -n 100   # Last 100 lines
python3 tests/ha_control.py logs -f       # Follow mode (tail -f)

# Check current position from both addon and HA
python3 tests/ha_control.py position

# Run 60-second sync check (API polling)
python3 tests/quick_sync_check.py --duration 60 --interval 200

# Control playback
python3 tests/ha_control.py play
python3 tests/ha_control.py pause
python3 tests/ha_control.py status

# Restart addon
python3 tests/ha_control.py restart-addon

# Full sync test with screenshots (uses venv for playwright)
cd tests && .venv/bin/python sync_test.py --checks 5 --interval 10
```

---

## Ground Control Addon

Task and project management UI for Home Assistant. Displays a Kanban board synced with `.tasks/` markdown files.

### Key Files

| File | Purpose |
|------|---------|
| `ground-control/app/main.py` | Backend API server |
| `ground-control/frontend/` | Web UI |
| `ground-control/config.yaml` | HA addon configuration |

### Features

- Kanban board UI
- Parse/sync `.tasks/` markdown files
- Project progress tracking
- File watching for external changes

### Version

Current: **v0.1.5**

Update version in `ground-control/config.yaml` when making changes.

---

## Repository Structure

```
ha-addons/
├── .claude/
│   └── sync/              # Agent sync system (MQTT)
│       ├── mqtt-sync.py   # Send/receive messages
│       ├── inbox/         # Messages from Major Tom
│       ├── outbox/        # Messages to Major Tom
│       └── archive/       # Processed messages
├── ground-control/        # Task management addon (v0.1.5)
├── lyric-scroll/          # Lyrics display addon (v0.5.16)
├── docs/                  # Design docs (mostly for lyric-scroll)
├── tests/                 # Test scripts
└── scripts/               # Utility scripts
```

## Versioning

When making changes to an addon:

1. Update version in `<addon>/config.yaml`
2. Update `<addon>/CHANGELOG.md`
3. Commit with version in message: `"Description (vX.Y.Z)"`
4. Push to trigger HA addon refresh
