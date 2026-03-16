# Home Assistant Addons

Custom Home Assistant addons for music visualization and task management.

## Addons

| Addon | Version | Description |
|-------|---------|-------------|
| [Lyric Scroll](lyric-scroll/) | v0.5.16 | Synchronized, scrolling karaoke-style lyrics for Music Assistant. Supports casting to Chromecast/Nest Hub. |
| [Ground Control](ground-control/) | v0.1.5 | Task and project management Kanban board, synced with `.tasks/` markdown files. |

## Installation

Add this repository to Home Assistant:

1. Go to **Settings > Add-ons > Add-on Store**
2. Click the three dots menu (top right) > **Repositories**
3. Add: `https://github.com/loydmilligan/ha-addons`
4. Find and install the addon you want

## Development

This repo uses a Claude Code agent (**GCA**) that coordinates with **Major Tom** (running in Home Assistant) via MQTT messaging. See `.claude/sync/README.md` for protocol details.

## License

MIT
