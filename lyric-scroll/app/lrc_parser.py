"""LRC format parser."""

import re
import logging
from typing import Optional
from models import LyricLine, LyricWord, Lyrics, TrackInfo

logger = logging.getLogger(__name__)

# Match [mm:ss.xx] or [mm:ss:xx] or [mm:ss]
TIMESTAMP_PATTERN = re.compile(r'\[(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?\]')

# Match <mm:ss.xx> for word-level timing
WORD_TIMESTAMP_PATTERN = re.compile(r'<(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?>')


def parse_timestamp(minutes: str, seconds: str, centiseconds: Optional[str]) -> int:
    """Convert timestamp components to milliseconds."""
    ms = int(minutes) * 60 * 1000
    ms += int(seconds) * 1000
    if centiseconds:
        # Handle both centiseconds (2 digits) and milliseconds (3 digits)
        if len(centiseconds) == 2:
            ms += int(centiseconds) * 10
        else:
            ms += int(centiseconds)
    return ms


def parse_lrc(content: str, source: str = "unknown", track: Optional[TrackInfo] = None) -> Lyrics:
    """Parse LRC content into structured Lyrics object."""
    lines: list[LyricLine] = []

    for line in content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        # Find all timestamps at the start of the line
        timestamps = []
        remaining = line

        while True:
            match = TIMESTAMP_PATTERN.match(remaining)
            if not match:
                break

            ts_ms = parse_timestamp(match.group(1), match.group(2), match.group(3))
            timestamps.append(ts_ms)
            remaining = remaining[match.end():]

        if not timestamps:
            # Skip lines without timestamps (metadata like [ar:Artist])
            continue

        text = remaining.strip()
        if not text:
            # Skip empty lyric lines
            continue

        # Check for word-level timing
        words: list[LyricWord] = []
        word_matches = list(WORD_TIMESTAMP_PATTERN.finditer(text))

        if word_matches:
            # Has word-level timing - parse it
            plain_text_parts = []
            last_end = 0

            for i, match in enumerate(word_matches):
                # Text before this timestamp
                if match.start() > last_end:
                    word_text = text[last_end:match.start()].strip()
                    if word_text:
                        plain_text_parts.append(word_text)

                word_ts = parse_timestamp(match.group(1), match.group(2), match.group(3))

                # Find word text (between this timestamp and next, or end)
                word_start = match.end()
                if i + 1 < len(word_matches):
                    word_end = word_matches[i + 1].start()
                else:
                    word_end = len(text)

                word_text = text[word_start:word_end].strip()
                if word_text:
                    words.append(LyricWord(timestamp_ms=word_ts, text=word_text))
                    plain_text_parts.append(word_text)

                last_end = word_end

            # Use plain text without timestamps
            text = ' '.join(plain_text_parts)

        # Create a LyricLine for each timestamp (handles lines like [00:10.00][00:20.00]text)
        for ts in timestamps:
            lines.append(LyricLine(
                timestamp_ms=ts,
                text=text,
                words=words.copy() if words else []
            ))

    # Sort by timestamp
    lines.sort(key=lambda l: l.timestamp_ms)

    return Lyrics(
        lines=lines,
        source=source,
        synced=True,
        track=track
    )


def create_unsynced_lyrics(text: str, source: str = "unknown", track: Optional[TrackInfo] = None) -> Lyrics:
    """Create lyrics without timing information."""
    lines = []
    for line_text in text.strip().split('\n'):
        line_text = line_text.strip()
        if line_text:
            lines.append(LyricLine(timestamp_ms=0, text=line_text))

    return Lyrics(
        lines=lines,
        source=source,
        synced=False,
        track=track
    )
