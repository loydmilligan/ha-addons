# Receiver Fallback Page Design

## Overview

The Chromecast receiver (`http://192.168.4.158:9123/receiver.html`) displays a fallback "clock" page when not showing lyrics. This document explains how to enhance that page with dynamic content like a custom title and recently played tracks with album art.

## Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│  Lyric Scroll   │  ── messages ──►   │  Cast Receiver  │
│     Addon       │                    │    (on Pi)      │
│                 │                    │                 │
│ - Tracks played │  {"recentTracks":  │ - Shows clock   │
│ - Album art URLs│    [...]}         │ - Shows recents │
│                 │                    │ - Shows lyrics  │
└─────────────────┘                    └─────────────────┘
```

The receiver already listens for custom messages on namespace `urn:x-cast:com.casttest.custom`. We just need to:
1. Add new message types for fallback content
2. Update the receiver HTML to display the content
3. Have the addon send the data

## Message Protocol

### Existing Messages
| Message | Description |
|---------|-------------|
| `{"loadUrl": "..."}` | Load URL in iframe (lyrics page) |
| `{"clearUrl": true}` | Clear iframe, show fallback |
| `{"message": "text"}` | Display text message |
| `{"background": "css"}` | Change background |

### New Messages to Add
| Message | Description |
|---------|-------------|
| `{"title": "Lyric Scroll"}` | Set the page title |
| `{"recentTracks": [...]}` | Update recently played list |
| `{"clearRecentTracks": true}` | Clear the list |

### Recent Track Object
```json
{
  "recentTracks": [
    {
      "title": "Good Flirts",
      "artist": "Baby Keem & Kendrick Lamar",
      "album": "The Hillbillies",
      "albumArt": "http://192.168.6.8:8099/api/albumart/abc123",
      "playedAt": "2026-03-12T02:21:00Z"
    }
  ]
}
```

---

## Implementation

### Step 1: Update Receiver HTML

**File:** `cast-receiver/public/receiver.html` (on Pi at 192.168.4.158)

**Repo:** https://github.com/loydmilligan/cast-receiver

#### Current Fallback Structure
```html
<div class="container" id="clockContainer">
  <div class="time" id="time">--:--:--</div>
  <div class="date" id="date">Loading...</div>
  <div class="message" id="message">Cast Test Active</div>
  <div class="dynamic-content" id="dynamic">Updates every second</div>
</div>
```

#### New Fallback Structure
```html
<div class="container" id="clockContainer">
  <!-- Header with custom title -->
  <div class="header">
    <h1 id="pageTitle">Lyric Scroll</h1>
  </div>

  <!-- Clock section -->
  <div class="clock-section">
    <div class="time" id="time">--:--:--</div>
    <div class="date" id="date">Loading...</div>
  </div>

  <!-- Recently played section -->
  <div class="recent-section" id="recentSection">
    <h2>Recently Played</h2>
    <div class="recent-tracks" id="recentTracks">
      <!-- Tracks inserted dynamically -->
    </div>
  </div>
</div>
```

#### CSS for Recently Played
```css
.header {
  margin-bottom: 30px;
}

.header h1 {
  font-size: 48px;
  font-weight: 300;
  opacity: 0.9;
}

.clock-section {
  margin-bottom: 40px;
}

.recent-section {
  max-width: 800px;
  margin: 0 auto;
}

.recent-section h2 {
  font-size: 24px;
  opacity: 0.7;
  margin-bottom: 20px;
}

.recent-tracks {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.track-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px 16px;
}

.track-art {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  object-fit: cover;
  background: rgba(255, 255, 255, 0.1);
}

.track-info {
  flex: 1;
  text-align: left;
}

.track-title {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 4px;
}

.track-artist {
  font-size: 16px;
  opacity: 0.7;
}

.track-album {
  font-size: 14px;
  opacity: 0.5;
  margin-top: 2px;
}

.track-time {
  font-size: 14px;
  opacity: 0.5;
}
```

#### JavaScript Message Handler
```javascript
// Add to existing message listener
context.addCustomMessageListener(NAMESPACE, (event) => {
  const data = event.data;

  // Existing handlers...
  if (data.loadUrl) { /* ... */ }
  if (data.clearUrl) { /* ... */ }

  // NEW: Set page title
  if (data.title) {
    document.getElementById('pageTitle').textContent = data.title;
  }

  // NEW: Update recently played tracks
  if (data.recentTracks) {
    updateRecentTracks(data.recentTracks);
  }

  // NEW: Clear recent tracks
  if (data.clearRecentTracks) {
    document.getElementById('recentTracks').innerHTML = '';
  }
});

// NEW: Function to render recent tracks
function updateRecentTracks(tracks) {
  const container = document.getElementById('recentTracks');
  container.innerHTML = '';

  tracks.slice(0, 5).forEach(track => {
    const item = document.createElement('div');
    item.className = 'track-item';

    const timeAgo = formatTimeAgo(track.playedAt);

    item.innerHTML = `
      <img class="track-art"
           src="${track.albumArt || ''}"
           alt=""
           onerror="this.style.display='none'">
      <div class="track-info">
        <div class="track-title">${escapeHtml(track.title)}</div>
        <div class="track-artist">${escapeHtml(track.artist)}</div>
        ${track.album ? `<div class="track-album">${escapeHtml(track.album)}</div>` : ''}
      </div>
      <div class="track-time">${timeAgo}</div>
    `;

    container.appendChild(item);
  });
}

function formatTimeAgo(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

---

### Step 2: Update Addon to Send Data

**File:** `lyric-scroll/app/main.py`

#### Add Recent Tracks Storage
```python
class LyricScrollApp:
    def __init__(self):
        # ... existing init ...
        self.recent_tracks = []  # Store last N tracks
        self.max_recent_tracks = 10
```

#### Track Recently Played
```python
async def _fetch_and_broadcast_lyrics(self, track):
    # ... existing lyrics fetching ...

    # Add to recent tracks
    self._add_recent_track(track)

    # Send to receiver if connected
    await self._update_receiver_recents()

def _add_recent_track(self, track):
    """Add track to recently played list."""
    track_data = {
        "title": track.title,
        "artist": track.artist,
        "album": getattr(track, 'album', ''),
        "albumArt": self._get_album_art_url(track),
        "playedAt": datetime.utcnow().isoformat() + "Z"
    }

    # Remove if already in list (re-add at top)
    self.recent_tracks = [
        t for t in self.recent_tracks
        if not (t['title'] == track_data['title'] and t['artist'] == track_data['artist'])
    ]

    # Add to front
    self.recent_tracks.insert(0, track_data)

    # Trim to max
    self.recent_tracks = self.recent_tracks[:self.max_recent_tracks]

def _get_album_art_url(self, track):
    """Get album art URL for track."""
    # Option 1: Use Music Assistant's album art if available
    # Option 2: Use a proxy endpoint in the addon
    # Option 3: Use a placeholder

    # Example: addon serves album art
    if hasattr(track, 'image_url') and track.image_url:
        return track.image_url

    # Fallback: no art
    return ""
```

#### Send to Receiver
```python
async def _update_receiver_recents(self):
    """Send recently played tracks to receiver."""
    if not self.caster:
        return

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.caster.send_message,
            {"recentTracks": self.recent_tracks}
        )
        logger.debug(f"Sent {len(self.recent_tracks)} recent tracks to receiver")
    except Exception as e:
        logger.error(f"Failed to send recent tracks: {e}")
```

#### Update Receiver Title on Connect
```python
async def _init_chromecast(self):
    # ... existing connection code ...

    # Set custom title
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.caster.send_message,
            {"title": "Lyric Scroll"}
        )
    except:
        pass
```

---

### Step 3: Add send_message to ChromecastCaster

**File:** `lyric-scroll/app/chromecast_caster.py`

The `send_message` method may already exist. If not:

```python
def send_message(self, data: dict) -> bool:
    """Send a custom message to the receiver."""
    if not self.controller:
        logger.error("No controller - not connected")
        return False

    try:
        self.controller.send(data)
        logger.debug(f"Sent message: {data}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False
```

---

### Step 4: Deploy Receiver Changes

After updating `cast-receiver/public/receiver.html`:

```bash
# From development machine
cd ~/Projects/cast-test
git add public/receiver.html
git commit -m "Add recently played list to fallback page"
git push

# Deploy to Pi
ssh pi "cd ~/cast-receiver && git pull && docker compose up -d --build"
```

---

## Album Art Considerations

### Option A: Direct URLs from Music Assistant
If MA provides album art URLs accessible from the Chromecast's network, use them directly.

### Option B: Proxy Through Addon
Create an endpoint in the addon that proxies album art:
```python
@routes.get('/api/albumart/{track_id}')
async def get_album_art(request):
    track_id = request.match_info['track_id']
    # Fetch from MA or cache
    # Return image with proper content-type
```

### Option C: Use External Service
Services like MusicBrainz or Discogs can provide album art by artist/album name.

### Option D: Placeholder
Use a generic music icon when no art is available:
```html
<img src="data:image/svg+xml,..." onerror="this.src='fallback.svg'">
```

---

## Testing

1. Update and deploy receiver to Pi
2. Update addon with recent tracks logic
3. Play a few songs
4. Clear the lyrics display (`clearUrl: true`)
5. Verify fallback shows title and recent tracks with album art

---

## Summary

| Component | Change |
|-----------|--------|
| `cast-receiver/public/receiver.html` | Add title, recent tracks HTML/CSS/JS |
| `lyric-scroll/app/main.py` | Track recent songs, send to receiver |
| `lyric-scroll/app/chromecast_caster.py` | Ensure `send_message()` works |
| Deploy | Push to GitHub, update Pi container |
