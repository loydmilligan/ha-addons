"""Track songs that don't have lyrics available."""

import json
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Store in addon's persistent data directory
MISSING_LYRICS_FILE = "/data/missing_lyrics.json"


class MissingLyricsTracker:
    """Track songs that couldn't find lyrics."""

    def __init__(self, file_path: str = MISSING_LYRICS_FILE):
        self.file_path = file_path
        self.missing: dict = {}
        self._load()

    def _load(self) -> None:
        """Load missing lyrics data from file."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    self.missing = json.load(f)
                logger.info(f"Loaded {len(self.missing)} missing lyrics entries")
        except Exception as e:
            logger.error(f"Failed to load missing lyrics: {e}")
            self.missing = {}

    def _save(self) -> None:
        """Save missing lyrics data to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.missing, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save missing lyrics: {e}")

    def _make_key(self, artist: str, title: str) -> str:
        """Create a unique key for a track."""
        return f"{artist.lower().strip()}|{title.lower().strip()}"

    def add(self, artist: str, title: str, album: str = "",
            album_art_url: str = "", entity_id: str = "") -> None:
        """Add a track to the missing lyrics list."""
        key = self._make_key(artist, title)

        if key not in self.missing:
            self.missing[key] = {
                "artist": artist,
                "title": title,
                "album": album,
                "album_art_url": album_art_url,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "play_count": 1,
                "entity_id": entity_id
            }
            logger.info(f"Added to missing lyrics: {artist} - {title}")
        else:
            # Update existing entry
            self.missing[key]["last_seen"] = datetime.now().isoformat()
            self.missing[key]["play_count"] = self.missing[key].get("play_count", 0) + 1
            if album and not self.missing[key].get("album"):
                self.missing[key]["album"] = album
            if album_art_url:
                self.missing[key]["album_art_url"] = album_art_url

        self._save()

    def remove(self, artist: str, title: str) -> bool:
        """Remove a track from the missing lyrics list (e.g., when lyrics are added)."""
        key = self._make_key(artist, title)
        if key in self.missing:
            del self.missing[key]
            self._save()
            logger.info(f"Removed from missing lyrics: {artist} - {title}")
            return True
        return False

    def get_all(self) -> list[dict]:
        """Get all missing lyrics entries, sorted by play count."""
        entries = list(self.missing.values())
        entries.sort(key=lambda x: x.get("play_count", 0), reverse=True)
        return entries

    def get_count(self) -> int:
        """Get the number of tracks with missing lyrics."""
        return len(self.missing)

    def clear(self) -> None:
        """Clear all missing lyrics entries."""
        self.missing = {}
        self._save()
        logger.info("Cleared all missing lyrics entries")
