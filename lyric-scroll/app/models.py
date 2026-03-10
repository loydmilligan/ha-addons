"""Data models for Lyric Scroll."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrackInfo:
    """Information about the currently playing track."""
    title: str
    artist: str
    album: str = ""
    duration_ms: int = 0

    def __eq__(self, other):
        if not isinstance(other, TrackInfo):
            return False
        return self.title == other.title and self.artist == other.artist

    def __hash__(self):
        return hash((self.title, self.artist))


@dataclass
class PlaybackState:
    """Current playback state from media player."""
    state: str  # playing, paused, idle, off
    position_ms: int = 0
    entity_id: str = ""
    track: Optional[TrackInfo] = None


@dataclass
class LyricWord:
    """A single word with timing (for enhanced LRC)."""
    timestamp_ms: int
    text: str


@dataclass
class LyricLine:
    """A single line of lyrics with timing."""
    timestamp_ms: int
    text: str
    words: list[LyricWord] = field(default_factory=list)


@dataclass
class Lyrics:
    """Complete lyrics for a track."""
    lines: list[LyricLine]
    source: str  # lrclib, musixmatch, genius, cache
    synced: bool  # True if has timing data
    track: Optional[TrackInfo] = None
