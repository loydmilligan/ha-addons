# Design Document: Lyric Scroll Home Assistant Addon

## Overview

Lyric Scroll is a Home Assistant addon that displays synchronized, karaoke-style lyrics for currently playing music. It monitors HA media_player entities and renders lyrics on a castable web interface.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Home Assistant                             │
│                                                                  │
│  ┌─────────────────┐         ┌─────────────────────────────┐    │
│  │  media_player   │         │    Lyric Scroll Addon       │    │
│  │    entities     │◀───────▶│                             │    │
│  │                 │  WS API │  ┌─────────────────────┐    │    │
│  │ - Spotify       │         │  │   Backend Server    │    │    │
│  │ - Chromecast    │         │  │   (Python/aiohttp)  │    │    │
│  │ - Sonos         │         │  │                     │    │    │
│  │ - etc.          │         │  │ - State subscriber  │    │    │
│  └─────────────────┘         │  │ - Lyrics fetcher    │    │    │
│                              │  │ - WebSocket server  │    │    │
│                              │  └──────────┬──────────┘    │    │
│                              │             │               │    │
│                              │  ┌──────────▼──────────┐    │    │
│                              │  │   Frontend (Web)    │    │    │
│                              │  │                     │    │    │
│                              │  │ - Karaoke renderer  │    │    │
│                              │  │ - Sync engine       │    │    │
│                              │  │ - Settings UI       │    │    │
│                              │  └─────────────────────┘    │    │
│                              └─────────────────────────────┘    │
│                                           │                      │
│                                           │ Ingress              │
│                                           ▼                      │
│                              ┌─────────────────────────┐         │
│                              │  Chromecast / Browser   │         │
│                              │  / Wall Tablet          │         │
│                              └─────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Backend Server

**Technology:** Python 3.11+ with aiohttp

**Responsibilities:**
- Connect to Home Assistant WebSocket API using Supervisor token
- Subscribe to `media_player` entity state changes
- Detect track changes (artist + title change)
- Fetch lyrics from external sources
- Parse LRC format into timed lyrics data structure
- Serve frontend static files
- Push lyrics and playback state to frontend via WebSocket

**Key Classes:**
```
HAClient           - WebSocket connection to HA, state subscription
LyricsFetcher      - Fetches lyrics from multiple sources with fallback
LRCParser          - Parses LRC format to structured data
SyncEngine         - Tracks playback position, handles seek/pause
WebServer          - aiohttp server for frontend + WebSocket
```

### 2. Lyrics Sources (Priority Order)

| Source | Type | Notes |
|--------|------|-------|
| LRCLIB | Free API | Community-driven, good coverage, timed lyrics |
| Musixmatch | API | Large database, may need token, timed lyrics |
| Genius | Scrape/API | Good coverage, plain text only (no timing) |
| Local cache | File | Previously fetched lyrics stored locally |

**Fallback Strategy:**
1. Check local cache
2. Try LRCLIB (free, timed)
3. Try Musixmatch (if configured)
4. Try Genius (plain text fallback)
5. Display "No lyrics found" message

### 3. LRC Format Handling

**Standard LRC:**
```
[00:12.34]First line of lyrics
[00:15.67]Second line of lyrics
```

**Enhanced LRC (word-level timing):**
```
[00:12.34]<00:12.34>First <00:12.80>line <00:13.10>of <00:13.40>lyrics
```

**Data Structure:**
```python
@dataclass
class LyricLine:
    timestamp_ms: int
    text: str
    words: list[LyricWord] | None  # For enhanced LRC

@dataclass
class LyricWord:
    timestamp_ms: int
    text: str

@dataclass
class Lyrics:
    lines: list[LyricLine]
    source: str
    synced: bool  # True if has timing, False for plain text
```

### 4. Sync Engine

**Challenges:**
- Media player position updates are not real-time (polled every ~1s)
- Network latency between music playback and display
- User may seek within track

**Approach:**
- On track start, record `(ha_position, local_timestamp)`
- Interpolate current position: `estimated_pos = ha_position + (now - local_timestamp)`
- On HA position update, re-anchor if drift > threshold (500ms)
- On seek detected (position jumps), re-anchor immediately
- Configurable offset for user to fine-tune sync

### 5. Frontend Architecture

**Technology:** Vanilla JS + CSS (no build step for simplicity)

**Components:**
```
KaraokeRenderer    - Renders lyrics with current line highlighted
SyncClient         - WebSocket connection to backend, time sync
SettingsPanel      - Configuration UI (offset, theme, font size)
AnimationEngine    - Smooth scrolling and transitions
```

**Rendering Modes:**
1. **Scroll Mode** - Lines scroll vertically, current line centered
2. **Page Mode** - Show N lines at a time, page flip at boundaries
3. **Focus Mode** - Only current line visible, large text

### 6. Configuration

**Addon Options (config.yaml):**
```yaml
media_players:
  - media_player.spotify_username
  - media_player.living_room_speaker
sync_offset_ms: 0
display_mode: scroll
theme: dark
font_size: large
```

**Runtime Settings (adjustable in UI):**
- Sync offset (±5 seconds)
- Font size
- Theme (dark/light/custom colors)
- Display mode
- Lines visible (for page mode)

## Data Flow

### Track Change Flow
```
1. HA media_player state changes (new track)
2. Backend receives state via WebSocket
3. Backend extracts artist + title
4. Backend fetches lyrics (cache → LRCLIB → fallbacks)
5. Backend parses LRC to structured data
6. Backend pushes lyrics to frontend via WebSocket
7. Frontend resets renderer with new lyrics
8. Frontend begins sync from position 0
```

### Playback Sync Flow
```
1. HA media_player updates position (every ~1s)
2. Backend receives position update
3. Backend calculates estimated real-time position
4. Backend pushes position to frontend
5. Frontend interpolates between updates
6. Frontend highlights appropriate line/word
```

## API Contracts

### Backend → Frontend WebSocket Messages

```typescript
// New track with lyrics
{
  type: "lyrics",
  data: {
    track: { title: string, artist: string, album: string },
    lyrics: LyricLine[],
    synced: boolean,
    duration_ms: number
  }
}

// Position update
{
  type: "position",
  data: {
    position_ms: number,
    state: "playing" | "paused" | "idle"
  }
}

// No lyrics found
{
  type: "no_lyrics",
  data: { track: { title: string, artist: string } }
}

// Playback stopped
{
  type: "idle"
}
```

### Frontend → Backend WebSocket Messages

```typescript
// Request resync
{ type: "resync" }

// Update settings
{
  type: "settings",
  data: { offset_ms: number, ... }
}
```

## File Structure

```
lyric-scroll/
├── config.yaml              # HA addon manifest
├── Dockerfile               # Addon container
├── run.sh                   # Container entrypoint
├── requirements.txt         # Python dependencies
│
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── ha_client.py         # HA WebSocket client
│   ├── lyrics_fetcher.py    # Multi-source lyrics fetching
│   ├── lrc_parser.py        # LRC parsing
│   ├── sync_engine.py       # Position tracking
│   └── web_server.py        # aiohttp server
│
├── frontend/
│   ├── index.html           # Main display page
│   ├── settings.html        # Settings UI
│   ├── css/
│   │   ├── karaoke.css      # Display styles
│   │   └── themes.css       # Theme definitions
│   └── js/
│       ├── karaoke.js       # Main renderer
│       ├── sync.js          # WebSocket sync client
│       └── settings.js      # Settings management
│
├── cache/                   # Cached lyrics (mounted volume)
│
└── docs/
    ├── DESIGN.md            # This document
    ├── UI_UX_SPEC.md        # UI/UX specification
    └── PROJECT_PLAN.md      # Implementation phases
```

## Security Considerations

- Addon runs in isolated Docker container
- Uses HA Supervisor API token (auto-provided)
- No external network access required except for lyrics APIs
- Lyrics cached locally to minimize API calls
- No user credentials stored (uses HA auth)

## Performance Considerations

- Lyrics cached to disk to avoid repeated API calls
- WebSocket for low-latency updates (no polling)
- Frontend uses requestAnimationFrame for smooth animation
- Debounce rapid state changes from HA
- Lazy load settings UI

## Future Enhancements (Out of Scope for MVP)

- Audio fingerprinting for vinyl/unknown sources
- Custom LRC file upload
- Lyrics editing/correction UI
- Multiple display instances (different rooms)
- Romanization for non-Latin scripts
- Translation overlay
- Ambient mode (color extraction from album art)
