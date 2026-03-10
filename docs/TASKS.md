# Lyric Scroll - Development Tasks

## Phase 0: Development Environment Setup

### 0.1 Repository Setup
- [ ] Initialize git repository (done)
- [ ] Create `.gitignore` for Python/Node artifacts
- [ ] Push repository to GitHub
- [ ] Add repository description and topics

### 0.2 Home Assistant Addon Repository Structure
- [ ] Create `repository.yaml` (addon repo metadata)
- [ ] Create addon folder structure: `lyric-scroll/`
- [ ] Create `lyric-scroll/config.yaml` (addon manifest)
- [ ] Create `lyric-scroll/CHANGELOG.md`
- [ ] Create `lyric-scroll/icon.png` (placeholder)
- [ ] Create `lyric-scroll/logo.png` (placeholder)

### 0.3 Connect to Home Assistant App Store
- [ ] Push initial addon structure to GitHub
- [ ] In HA: Settings → Add-ons → Add-on Store → ⋮ → Repositories
- [ ] Add GitHub repo URL as custom repository
- [ ] Verify addon appears in App Store
- [ ] Test install/uninstall cycle

### 0.4 Development Workflow
- [ ] Document the dev workflow in CONTRIBUTING.md:
  - Make changes locally
  - Commit and push to GitHub
  - In HA: Add-on → Lyric Scroll → Rebuild
  - Check logs for errors
- [ ] Set up VS Code workspace with Python extensions
- [ ] Configure local Python environment for IDE support

---

## Phase 1: Foundation

### 1.1 Python Project Structure
- [ ] Create `lyric-scroll/app/` directory
- [ ] Create `lyric-scroll/app/__init__.py`
- [ ] Create `lyric-scroll/app/main.py` (entry point)
- [ ] Create `lyric-scroll/requirements.txt`:
  ```
  aiohttp>=3.9.0
  aiofiles>=23.0.0
  pyyaml>=6.0
  ```
- [ ] Create `lyric-scroll/Dockerfile`
- [ ] Create `lyric-scroll/run.sh` (container entrypoint)

### 1.2 Addon Configuration
- [ ] Define `config.yaml` options schema:
  - `media_players` (list of entity IDs)
  - `sync_offset_ms` (integer, default 0)
  - `display_mode` (enum: scroll/page/focus)
  - `theme` (enum: dark/light/oled)
- [ ] Set up Ingress for web UI access
- [ ] Configure required HA API permissions

### 1.3 Home Assistant WebSocket Client
- [ ] Create `lyric-scroll/app/ha_client.py`
- [ ] Implement `HAClient` class with async context manager
- [ ] Implement `connect()` - establish WebSocket connection
- [ ] Implement `authenticate()` - use Supervisor token
- [ ] Implement `subscribe_entities()` - subscribe to media_player states
- [ ] Implement `_handle_message()` - parse incoming state updates
- [ ] Implement auto-reconnect with exponential backoff
- [ ] Add logging for connection events and errors
- [ ] Test: verify connection to HA instance

### 1.4 Media Player State Parsing
- [ ] Create `lyric-scroll/app/models.py` for data classes
- [ ] Define `TrackInfo` dataclass (title, artist, album, duration_ms)
- [ ] Define `PlaybackState` dataclass (state, position_ms, timestamp)
- [ ] Implement `parse_media_player_state()` function
- [ ] Handle missing attributes gracefully
- [ ] Detect track changes (artist + title changed)
- [ ] Test: log track info when music plays

### 1.5 LRCLIB Integration
- [ ] Create `lyric-scroll/app/lyrics_fetcher.py`
- [ ] Implement `LyricsFetcher` class
- [ ] Implement `fetch_from_lrclib()`:
  - GET `https://lrclib.net/api/get?artist={}&track={}`
  - Parse JSON response
  - Extract synced lyrics (syncedLyrics field)
  - Fall back to plain lyrics if no synced
- [ ] Add request timeout (10 seconds)
- [ ] Handle HTTP errors gracefully
- [ ] Test: fetch lyrics for known song

### 1.6 Local Lyrics Cache
- [ ] Create `lyric-scroll/app/cache.py`
- [ ] Implement `LyricsCache` class
- [ ] Define cache file naming: `{artist}_{title}.lrc` (sanitized)
- [ ] Implement `get()` - read from cache directory
- [ ] Implement `set()` - write to cache directory
- [ ] Implement `has()` - check if cached
- [ ] Use `/data/cache/` directory (persisted volume)
- [ ] Test: cache hit/miss behavior

### 1.7 LRC Parser
- [ ] Create `lyric-scroll/app/lrc_parser.py`
- [ ] Define `LyricLine` dataclass (timestamp_ms, text)
- [ ] Define `Lyrics` dataclass (lines, source, synced)
- [ ] Implement `parse_lrc()` function
- [ ] Parse timestamp format: `[mm:ss.xx]` or `[mm:ss:xx]`
- [ ] Handle multiple timestamps per line
- [ ] Sort lines by timestamp
- [ ] Handle malformed lines (skip with warning)
- [ ] Test: parse sample LRC files

### 1.8 Web Server Setup
- [ ] Create `lyric-scroll/app/web_server.py`
- [ ] Implement `WebServer` class
- [ ] Set up aiohttp Application
- [ ] Serve static files from `/frontend/`
- [ ] Create WebSocket endpoint `/ws`
- [ ] Implement client connection tracking
- [ ] Implement broadcast to all clients
- [ ] Test: server starts and serves index.html

### 1.9 Backend Integration
- [ ] Wire up components in `main.py`:
  - Initialize HAClient
  - Initialize LyricsFetcher with cache
  - Initialize WebServer
  - Connect state changes to lyrics fetching
- [ ] On track change: fetch lyrics → broadcast to clients
- [ ] On position update: broadcast to clients
- [ ] Handle graceful shutdown (SIGTERM)
- [ ] Test: end-to-end flow in HA

### 1.10 Minimal Frontend
- [ ] Create `lyric-scroll/frontend/index.html`
- [ ] Create `lyric-scroll/frontend/css/main.css`
- [ ] Create `lyric-scroll/frontend/js/app.js`
- [ ] Implement WebSocket connection to backend
- [ ] Display lyrics as vertical list
- [ ] Highlight current line based on position
- [ ] Basic dark theme (black bg, white text)
- [ ] Show track info at bottom
- [ ] Show loading/idle/no-lyrics states
- [ ] Test: lyrics display and highlight correctly

---

## Phase 2: Sync Engine

### 2.1 Position Tracking
- [ ] Create `lyric-scroll/app/sync_engine.py`
- [ ] Implement `SyncEngine` class
- [ ] Store anchor point: `(ha_position_ms, local_timestamp)`
- [ ] Implement `update_position()` - called on HA updates
- [ ] Implement `get_current_position()` - interpolated position
- [ ] Test: position stays accurate between updates

### 2.2 Drift Correction
- [ ] Detect drift > threshold (configurable, default 500ms)
- [ ] Re-anchor when drift detected
- [ ] Log drift corrections for debugging
- [ ] Test: artificially delay updates, verify correction

### 2.3 Seek Detection
- [ ] Detect position jumps (|new - expected| > 2000ms)
- [ ] Immediately re-anchor on seek
- [ ] Notify frontend of seek event
- [ ] Test: seek in Spotify, verify lyrics jump correctly

### 2.4 Play/Pause Handling
- [ ] Track playback state (playing/paused/idle)
- [ ] Pause interpolation when state is paused
- [ ] Resume from correct position on play
- [ ] Test: pause/resume maintains sync

### 2.5 User Sync Offset
- [ ] Add offset_ms to config options
- [ ] Apply offset in `get_current_position()`
- [ ] Persist offset changes to config
- [ ] Test: adjust offset, verify lyrics shift

### 2.6 Frontend Smooth Scrolling
- [ ] Implement `SyncClient` class in JS
- [ ] Use requestAnimationFrame for position updates
- [ ] Interpolate position client-side between server updates
- [ ] Implement smooth scroll to current line (CSS scroll-behavior or JS)
- [ ] Test: scrolling feels smooth

---

## Phase 3: Display Modes & Themes

### 3.1 CSS Foundation
- [ ] Create `lyric-scroll/frontend/css/variables.css`
- [ ] Define CSS custom properties for theming
- [ ] Define typography scale
- [ ] Define spacing scale
- [ ] Define animation durations

### 3.2 Scroll Mode
- [ ] Implement `ScrollRenderer` class
- [ ] Render all lyrics vertically
- [ ] Center current line in viewport
- [ ] Apply dim styling to non-current lines
- [ ] Animate scroll with CSS transition
- [ ] Test: smooth scrolling behavior

### 3.3 Page Mode
- [ ] Implement `PageRenderer` class
- [ ] Split lyrics into pages (N lines each)
- [ ] Track current page based on current line
- [ ] Render only current page
- [ ] Add page flip animation (crossfade)
- [ ] Add page indicator dots (optional)
- [ ] Test: page transitions work correctly

### 3.4 Focus Mode
- [ ] Implement `FocusRenderer` class
- [ ] Show only current line
- [ ] Large centered text
- [ ] Fade transition between lines
- [ ] Test: transitions are smooth

### 3.5 Theme: Dark (Default)
- [ ] Implement dark theme CSS variables
- [ ] Black background (#0a0a0a)
- [ ] White text for current line
- [ ] Gray text for other lines
- [ ] Blue accent color

### 3.6 Theme: Light
- [ ] Implement light theme CSS variables
- [ ] White background
- [ ] Dark text
- [ ] Appropriate contrast ratios

### 3.7 Theme: OLED
- [ ] Implement OLED theme CSS variables
- [ ] Pure black background (#000000)
- [ ] High contrast text
- [ ] Green accent color

### 3.8 Theme Switching
- [ ] Add theme class to body element
- [ ] Implement `setTheme()` function
- [ ] Persist theme to localStorage
- [ ] Load theme on page init
- [ ] Test: switching themes works

### 3.9 Font Size Options
- [ ] Define size scale (small/medium/large/xlarge)
- [ ] Implement `setFontSize()` function
- [ ] Apply scale factor to base sizes
- [ ] Persist to localStorage
- [ ] Test: all sizes readable

---

## Phase 4: Settings UI

### 4.1 Settings Panel Structure
- [ ] Create settings panel HTML structure
- [ ] Create `lyric-scroll/frontend/css/settings.css`
- [ ] Create `lyric-scroll/frontend/js/settings.js`
- [ ] Implement slide-in animation
- [ ] Add backdrop overlay
- [ ] Add close button

### 4.2 Settings Toggle
- [ ] Add settings icon to info bar
- [ ] Implement open/close toggle
- [ ] Keyboard shortcut (Escape to close)
- [ ] Test: panel opens/closes smoothly

### 4.3 Display Section
- [ ] Add "Display Mode" dropdown (Scroll/Page/Focus)
- [ ] Add "Theme" dropdown (Dark/Light/OLED)
- [ ] Add "Font Size" slider
- [ ] Wire up change handlers
- [ ] Test: changes apply immediately

### 4.4 Sync Section
- [ ] Add "Sync Offset" slider (-5s to +5s)
- [ ] Add fine-tune buttons (+/- 50ms)
- [ ] Display current offset value
- [ ] Add reset button
- [ ] Test: offset adjustments work

### 4.5 Settings Persistence
- [ ] Save all settings to localStorage
- [ ] Send settings to backend via WebSocket
- [ ] Backend persists to addon options
- [ ] Load settings on page init
- [ ] Test: settings survive page reload

---

## Phase 5: Enhanced Features

### 5.1 Enhanced LRC (Word Timing)
- [ ] Extend LRC parser for word timing: `<mm:ss.xx>`
- [ ] Define `LyricWord` dataclass
- [ ] Add words array to `LyricLine`
- [ ] Test: parse enhanced LRC correctly

### 5.2 Word-by-Word Highlighting
- [ ] Render individual word spans
- [ ] Highlight words based on timing
- [ ] Smooth transition between words
- [ ] Test: word highlighting syncs correctly

### 5.3 Musixmatch Integration (Optional)
- [ ] Add Musixmatch token to config options
- [ ] Implement `fetch_from_musixmatch()`
- [ ] Add to fetcher priority chain
- [ ] Test: fetches when LRCLIB fails

### 5.4 Genius Integration (Plain Text)
- [ ] Implement `fetch_from_genius()`
- [ ] Scrape or use API for plain lyrics
- [ ] Use as final fallback
- [ ] Display plain lyrics without timing
- [ ] Test: works for obscure songs

### 5.5 Connection Error Handling
- [ ] Display connection lost indicator
- [ ] Implement auto-reconnect in frontend
- [ ] Show reconnecting status
- [ ] Preserve last lyrics during reconnect
- [ ] Test: disconnect/reconnect scenario

### 5.6 Accessibility
- [ ] Add `prefers-reduced-motion` support
- [ ] Disable animations when set
- [ ] Add keyboard navigation (arrow keys)
- [ ] Ensure focus indicators visible
- [ ] Test: verify with reduced motion

---

## Phase 6: Production Ready

### 6.1 Unit Tests
- [ ] Set up pytest
- [ ] Test `LRCParser` with various inputs
- [ ] Test `SyncEngine` position calculations
- [ ] Test `LyricsCache` operations
- [ ] Test `parse_media_player_state()`

### 6.2 Integration Tests
- [ ] Test HAClient connection (mock HA)
- [ ] Test LyricsFetcher with mock APIs
- [ ] Test end-to-end lyrics flow

### 6.3 Documentation
- [ ] Write README.md with screenshots
- [ ] Write installation guide
- [ ] Write configuration guide
- [ ] Write troubleshooting FAQ
- [ ] Create demo GIF

### 6.4 Addon Repository Polish
- [ ] Create proper icon.png (512x512)
- [ ] Create proper logo.png (400x200)
- [ ] Update CHANGELOG.md
- [ ] Set version to 1.0.0
- [ ] Add license file

### 6.5 Final Testing
- [ ] Test with Spotify Connect
- [ ] Test with Chromecast
- [ ] Test with Sonos (if available)
- [ ] Test casting to TV
- [ ] Test on mobile browser
- [ ] Test on tablet

---

## Quick Reference: Dev Workflow

```bash
# 1. Make changes locally
code .

# 2. Commit and push
git add -A && git commit -m "description" && git push

# 3. In Home Assistant (192.168.6.8:8123)
#    Settings → Add-ons → Lyric Scroll → Rebuild

# 4. Check logs
#    Settings → Add-ons → Lyric Scroll → Logs

# 5. Access UI via Ingress
#    Click "Open Web UI" in addon page
```

## File Checklist for Phase 0 + 1

```
lyric-scroll/
├── repository.yaml          # Phase 0.2
├── lyric-scroll/
│   ├── config.yaml          # Phase 0.2, 1.2
│   ├── Dockerfile           # Phase 1.1
│   ├── run.sh               # Phase 1.1
│   ├── CHANGELOG.md         # Phase 0.2
│   ├── icon.png             # Phase 0.2
│   ├── logo.png             # Phase 0.2
│   ├── requirements.txt     # Phase 1.1
│   ├── app/
│   │   ├── __init__.py      # Phase 1.1
│   │   ├── main.py          # Phase 1.1, 1.9
│   │   ├── models.py        # Phase 1.4
│   │   ├── ha_client.py     # Phase 1.3
│   │   ├── lyrics_fetcher.py# Phase 1.5
│   │   ├── cache.py         # Phase 1.6
│   │   ├── lrc_parser.py    # Phase 1.7
│   │   └── web_server.py    # Phase 1.8
│   └── frontend/
│       ├── index.html       # Phase 1.10
│       ├── css/
│       │   └── main.css     # Phase 1.10
│       └── js/
│           └── app.js       # Phase 1.10
└── docs/
    ├── DESIGN.md
    ├── UI_UX_SPEC.md
    ├── PROJECT_PLAN.md
    └── TASKS.md
```
