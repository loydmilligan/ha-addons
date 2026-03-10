"""Fetch lyrics from various sources."""

import logging
import aiohttp
from typing import Optional
from urllib.parse import quote

from models import TrackInfo, Lyrics
from lrc_parser import parse_lrc, create_unsynced_lyrics
from cache import LyricsCache

logger = logging.getLogger(__name__)

LRCLIB_API = "https://lrclib.net/api/get"
REQUEST_TIMEOUT = 10


class LyricsFetcher:
    """Fetch lyrics from multiple sources with caching."""

    def __init__(self, cache: Optional[LyricsCache] = None):
        self.cache = cache or LyricsCache()
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            )
        return self._session

    async def close(self) -> None:
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch(self, track: TrackInfo) -> Optional[Lyrics]:
        """Fetch lyrics for a track, trying cache first then APIs."""

        # Try cache first
        cached = await self.cache.get(track.artist, track.title)
        if cached:
            return parse_lrc(cached, source="cache", track=track)

        # Try LRCLIB
        lyrics = await self._fetch_lrclib(track)
        if lyrics:
            return lyrics

        # TODO: Add more sources (Musixmatch, Genius)

        logger.info(f"No lyrics found for: {track.artist} - {track.title}")
        return None

    async def _fetch_lrclib(self, track: TrackInfo) -> Optional[Lyrics]:
        """Fetch lyrics from LRCLIB API."""
        try:
            session = await self._get_session()

            params = {
                "artist_name": track.artist,
                "track_name": track.title,
            }
            if track.album:
                params["album_name"] = track.album
            if track.duration_ms > 0:
                params["duration"] = track.duration_ms // 1000

            logger.info(f"Fetching from LRCLIB: {track.artist} - {track.title}")

            async with session.get(LRCLIB_API, params=params) as response:
                if response.status == 404:
                    logger.info("LRCLIB: No lyrics found")
                    return None

                if response.status != 200:
                    logger.warning(f"LRCLIB error: {response.status}")
                    return None

                data = await response.json()

                # Prefer synced lyrics
                if data.get("syncedLyrics"):
                    lrc_content = data["syncedLyrics"]
                    # Cache it
                    await self.cache.set(track.artist, track.title, lrc_content)
                    return parse_lrc(lrc_content, source="lrclib", track=track)

                # Fall back to plain lyrics
                if data.get("plainLyrics"):
                    logger.info("LRCLIB: Using plain lyrics (no timing)")
                    return create_unsynced_lyrics(
                        data["plainLyrics"],
                        source="lrclib",
                        track=track
                    )

                return None

        except aiohttp.ClientError as e:
            logger.error(f"LRCLIB request error: {e}")
            return None
        except Exception as e:
            logger.error(f"LRCLIB unexpected error: {e}")
            return None
