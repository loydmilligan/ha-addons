# Project Plan: Lyric Scroll

## Overview

This document outlines the implementation phases for Lyric Scroll, a Home Assistant addon for synchronized karaoke-style lyrics display.

## Phase 1: Foundation

**Goal:** Minimal working addon that can display lyrics for a playing track.

### Tasks

#### 1.1 Project Setup
- [ ] Initialize Python project structure
- [ ] Create `requirements.txt` with dependencies:
  - aiohttp
  - aiofiles
  - pyyaml
- [ ] Create Home Assistant addon configuration (`config.yaml`)
- [ ] Create Dockerfile for addon container
- [ ] Create `run.sh` entrypoint script

#### 1.2 Home Assistant Client
- [ ] Implement `HAClient` class
- [ ] Connect to HA WebSocket API using Supervisor token
- [ ] Subscribe to media_player entity state changes
- [ ] Parse media_player attributes (title, artist, position, state)
- [ ] Handle reconnection on disconnect

#### 1.3 Basic Lyrics Fetching
- [ ] Implement `LyricsFetcher` class
- [ ] Integrate LRCLIB API (primary source)
- [ ] Implement simple file-based cache
- [ ] Handle "no lyrics found" gracefully

#### 1.4 LRC Parser
- [ ] Implement `LRCParser` class
- [ ] Parse standard LRC format `[mm:ss.xx]text`
- [ ] Convert to `LyricLine` data structure
- [ ] Handle malformed LRC gracefully

#### 1.5 Basic Web Server
- [ ] Implement `WebServer` class with aiohttp
- [ ] Serve static frontend files
- [ ] WebSocket endpoint for frontend connection
- [ ] Push lyrics data to connected clients

#### 1.6 Minimal Frontend
- [ ] Create `index.html` with basic structure
- [ ] Implement WebSocket connection to backend
- [ ] Display lyrics as simple list
- [ ] Highlight current line based on position
- [ ] Basic dark theme styling

### Deliverables
- Addon installs and runs in Home Assistant
- Connects to configured media_player
- Fetches and displays lyrics (line-by-line highlight)
- Basic but functional UI

---

## Phase 2: Sync Engine

**Goal:** Accurate, smooth lyrics synchronization.

### Tasks

#### 2.1 Position Interpolation
- [ ] Implement `SyncEngine` class
- [ ] Track playback position with local timestamps
- [ ] Interpolate position between HA updates
- [ ] Re-anchor on drift > 500ms

#### 2.2 Seek Detection
- [ ] Detect position jumps (seek)
- [ ] Immediately re-sync on seek
- [ ] Handle backward seeks correctly

#### 2.3 Play/Pause Handling
- [ ] Track play/pause state
- [ ] Pause interpolation when paused
- [ ] Resume correctly on play

#### 2.4 User Offset
- [ ] Add configurable sync offset (±5000ms)
- [ ] Apply offset to all position calculations
- [ ] Persist offset to config

#### 2.5 Frontend Sync
- [ ] Implement smooth scrolling to current line
- [ ] Use requestAnimationFrame for animations
- [ ] Handle rapid position updates gracefully

### Deliverables
- Lyrics stay in sync during normal playback
- Seeking works correctly
- User can fine-tune offset
- Smooth scrolling animation

---

## Phase 3: Display Modes & Themes

**Goal:** Multiple viewing modes and visual customization.

### Tasks

#### 3.1 Scroll Mode (Default)
- [ ] Implement vertical scrolling renderer
- [ ] Center current line in viewport
- [ ] Dim non-current lines
- [ ] Smooth scroll transitions

#### 3.2 Page Mode
- [ ] Implement paged renderer
- [ ] Configurable lines per page
- [ ] Page flip animation
- [ ] Page indicator dots

#### 3.3 Focus Mode
- [ ] Implement single-line renderer
- [ ] Large centered text
- [ ] Fade transitions between lines

#### 3.4 Theme System
- [ ] Implement CSS custom properties for theming
- [ ] Create Dark theme (default)
- [ ] Create Light theme
- [ ] Create OLED theme
- [ ] Theme switcher in UI

#### 3.5 Font Size Options
- [ ] Implement font size scaling
- [ ] Small / Medium / Large / Extra Large options
- [ ] Persist preference

### Deliverables
- Three working display modes
- Three color themes
- Adjustable font sizes
- All settings persist

---

## Phase 4: Settings UI

**Goal:** User-friendly configuration interface.

### Tasks

#### 4.1 Settings Panel
- [ ] Create settings panel overlay
- [ ] Slide-in animation
- [ ] Section organization (Display, Sync, Highlight)

#### 4.2 Display Settings
- [ ] Mode selector dropdown
- [ ] Theme selector dropdown
- [ ] Font size slider
- [ ] Lines per page (page mode only)

#### 4.3 Sync Settings
- [ ] Offset slider (-5s to +5s)
- [ ] Fine-tune buttons (+/- 50ms)
- [ ] Test button (plays sample)
- [ ] Reset to default

#### 4.4 Highlight Settings
- [ ] Style radio buttons (Bright, Glow, Underline, Color)
- [ ] Live preview of selection

#### 4.5 Settings Persistence
- [ ] Save to localStorage
- [ ] Sync to backend config
- [ ] Load on page init

### Deliverables
- Complete settings UI
- All options functional
- Settings persist across sessions

---

## Phase 5: Enhanced Features

**Goal:** Polish and additional lyrics sources.

### Tasks

#### 5.1 Enhanced LRC Support
- [ ] Parse word-level timing `<mm:ss.xx>`
- [ ] Implement word-by-word highlighting
- [ ] Karaoke wipe effect (optional)

#### 5.2 Additional Lyrics Sources
- [ ] Integrate Musixmatch API (optional config)
- [ ] Integrate Genius API (plain text fallback)
- [ ] Source priority configuration

#### 5.3 Cache Management
- [ ] View cached lyrics count
- [ ] Clear cache option
- [ ] Cache size limit

#### 5.4 Error Handling
- [ ] Connection lost indicator
- [ ] Auto-reconnect with backoff
- [ ] Graceful degradation

#### 5.5 Accessibility
- [ ] Reduced motion support
- [ ] Keyboard navigation
- [ ] Minimum contrast compliance
- [ ] Screen reader announcements

### Deliverables
- Word-level karaoke (when available)
- Multiple lyrics sources
- Robust error handling
- Accessible interface

---

## Phase 6: Production Ready

**Goal:** Ready for public release.

### Tasks

#### 6.1 Testing
- [ ] Unit tests for LRC parser
- [ ] Unit tests for sync engine
- [ ] Integration tests for HA client
- [ ] Manual testing on various media players

#### 6.2 Documentation
- [ ] README with installation instructions
- [ ] Configuration guide
- [ ] Troubleshooting guide
- [ ] Screenshots/demo GIF

#### 6.3 Home Assistant Integration
- [ ] Addon repository setup
- [ ] Icon and logo
- [ ] Changelog
- [ ] Version numbering

#### 6.4 Performance Optimization
- [ ] Profile and optimize sync engine
- [ ] Minimize DOM updates
- [ ] Lazy load settings panel
- [ ] Compress static assets

#### 6.5 Final Polish
- [ ] Cross-browser testing
- [ ] Mobile/tablet testing
- [ ] Chromecast testing
- [ ] Edge case handling

### Deliverables
- Production-ready addon
- Published to addon repository
- Complete documentation
- Tested across platforms

---

## Timeline Estimates

| Phase | Complexity | Dependencies |
|-------|------------|--------------|
| Phase 1: Foundation | Medium | None |
| Phase 2: Sync Engine | High | Phase 1 |
| Phase 3: Display Modes | Medium | Phase 1 |
| Phase 4: Settings UI | Medium | Phase 3 |
| Phase 5: Enhanced Features | Medium | Phase 2, 4 |
| Phase 6: Production Ready | Low | All phases |

**Note:** Phases 2 and 3 can be developed in parallel after Phase 1 is complete.

---

## Tech Stack Summary

### Backend
- Python 3.11+
- aiohttp (async HTTP/WebSocket server)
- aiofiles (async file I/O)
- PyYAML (configuration)

### Frontend
- Vanilla JavaScript (ES6+)
- CSS3 with custom properties
- No build step required

### Infrastructure
- Docker container
- Home Assistant Supervisor API
- Home Assistant Ingress for access

---

## Risk Considerations

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| HA WebSocket API changes | High | Pin HA version compatibility, test on updates |
| Lyrics API rate limits | Medium | Aggressive caching, multiple sources |
| Sync accuracy varies by player | Medium | User-adjustable offset, per-player config |
| Browser compatibility | Low | Target modern browsers only, test major browsers |

### Scope Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Feature creep | Medium | Strict MVP scope, defer to "Future" list |
| Perfect sync expectations | Medium | Document limitations, provide offset control |

---

## Success Metrics

### MVP Success
- Addon installs without errors
- Lyrics display for Spotify media_player
- Sync is "good enough" (within 500ms)
- Basic UI is usable

### Full Release Success
- Works with 3+ media player types
- Sync accuracy within 200ms
- Settings fully functional
- No critical bugs for 2 weeks

---

## Next Steps

1. **Set up development environment**
   - Home Assistant dev instance
   - VS Code with Python extensions
   - Docker for addon testing

2. **Begin Phase 1.1: Project Setup**
   - Create file structure
   - Initialize Python project
   - Create addon manifest

3. **Implement HA Client (1.2)**
   - This is the core integration point
   - Test with real media_player entities
