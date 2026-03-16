# Lyric Scroll

Synchronized, scrolling karaoke-style lyrics for Music Assistant in Home Assistant.

## Overview

Lyric Scroll displays real-time synchronized lyrics for music playing through Music Assistant. It automatically fetches lyrics from LRCLIB and syncs them with your music playback. Supports casting to Chromecast and Nest Hub displays.

## Features

- **Synchronized Lyrics** - Line-by-line highlighting synced with music playback
- **Multiple Display Modes** - Scroll, Page, or Focus mode
- **Chromecast Support** - Cast lyrics to any Google Cast device
- **Auto Lyrics Fetch** - Automatically fetches from LRCLIB database
- **LRC Export** - Export lyrics to network share for offline access
- **Dark/Light/OLED Themes** - Multiple visual themes
- **Adjustable Sync** - Fine-tune timing with offset controls

## Accessing the UI

### Ingress Panel (Recommended)
Click "Lyrics" in the Home Assistant sidebar.

### Direct URL
Access directly at:
```
http://YOUR_HA_IP:8099
```

### Cast to Display
Cast the lyrics to a Chromecast or Nest Hub from the settings menu.

## Display Modes

| Mode | Description |
|------|-------------|
| **Scroll** | Lyrics scroll smoothly, current line centered |
| **Page** | Shows a page of lyrics at a time |
| **Focus** | Only shows current and nearby lines |

## Configuration

### Addon Options

| Option | Default | Description |
|--------|---------|-------------|
| `media_players` | `[]` | List of Music Assistant player entity IDs to monitor |
| `sync_offset_ms` | `0` | Global timing offset in milliseconds (+ = later, - = earlier) |
| `display_mode` | `scroll` | Display mode: scroll, page, or focus |
| `theme` | `dark` | Visual theme: dark, light, or oled |
| `font_size` | `large` | Font size: small, medium, large, or xlarge |
| `cast_app_id` | `""` | Custom Cast app ID (leave empty for default) |
| `lrc_export_enabled` | `false` | Export LRC files to network share |

### In-App Settings

Additional settings are available in the slide-out settings panel:
- Per-song sync adjustment
- Cast device selection
- Manual lyric refresh

## Lyrics Sources

Lyrics are fetched from [LRCLIB](https://lrclib.net/), a community database of synchronized lyrics. The addon:

1. Detects currently playing song from Music Assistant
2. Searches LRCLIB by artist and title
3. Downloads synced LRC if available
4. Falls back to plain lyrics if no sync available
5. Caches lyrics locally for faster loading

## Chromecast Setup

To cast lyrics to a Google Cast device:

1. **Register a Cast App** (one-time setup):
   - Go to [Google Cast SDK Console](https://cast.google.com/publish)
   - Create a custom receiver app pointing to your receiver URL
   - Note the App ID

2. **Configure the addon**:
   - Set `cast_app_id` in addon configuration
   - Restart the addon

3. **Cast from the UI**:
   - Open settings in the lyrics UI
   - Select your Cast device
   - Click "Cast"

### Cast Architecture

The addon uses a shell/container receiver pattern:
- Receiver hosts on a separate device (e.g., Raspberry Pi)
- Lyrics load in an iframe within the receiver
- Receiver shows a clock when no song is playing

## LRC Export

Enable `lrc_export_enabled` to save lyrics to a network share:

1. Configure the addon to mount your share
2. LRC files save as `Artist - Title.lrc`
3. Useful for offline access or editing

## Troubleshooting

### No lyrics showing
1. Check that Music Assistant is playing music
2. Verify the player entity is in `media_players` list
3. Song may not have synced lyrics in LRCLIB
4. Check addon logs for fetch errors

### Lyrics out of sync
1. Use the sync adjustment in settings (+/- seconds)
2. Set `sync_offset_ms` in addon config for global offset
3. Some songs have inaccurate timestamps in LRCLIB

### Cast not working
1. Verify Cast App ID is correct
2. Check that receiver URL is accessible
3. Cast device must be on same network
4. Check browser console for Cast SDK errors

### UI not loading
1. Try direct URL: `http://YOUR_HA_IP:8099`
2. Clear browser cache
3. Restart the addon
4. Check addon logs

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main lyrics UI |
| `/ws` | WebSocket for real-time updates |
| `/api/settings` | Get/update settings |
| `/api/ma/players` | List Music Assistant players |
| `/api/ma/displays` | List Cast displays |

## Integration with Music Assistant

Lyric Scroll monitors Music Assistant players via the HA WebSocket API. It detects:
- Song changes (artist, title, album)
- Playback position for sync
- Play/pause state

Configure your MA player entity IDs in the addon options.

## Support

- **Repository**: https://github.com/loydmilligan/ha-addons
- **Issues**: https://github.com/loydmilligan/ha-addons/issues
- **LRCLIB**: https://lrclib.net/ (lyrics database)
