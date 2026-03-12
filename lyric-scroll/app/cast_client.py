"""Direct Chromecast control using pychromecast."""

import logging
from typing import Optional
import pychromecast

logger = logging.getLogger(__name__)

# Cache discovered chromecasts
_chromecasts: dict = {}
_browser = None


def discover_chromecasts(timeout: float = 5.0) -> dict:
    """Discover Chromecast devices on the network.

    Returns dict mapping friendly_name -> Chromecast object
    """
    global _chromecasts, _browser

    try:
        chromecasts, browser = pychromecast.get_chromecasts(timeout=timeout)
        _browser = browser
        _chromecasts = {cc.cast_info.friendly_name: cc for cc in chromecasts}
        logger.info(f"Discovered {len(_chromecasts)} Chromecast(s): {list(_chromecasts.keys())}")
        return _chromecasts
    except Exception as e:
        logger.error(f"Chromecast discovery error: {e}")
        return {}


def get_chromecast(friendly_name: str) -> Optional[pychromecast.Chromecast]:
    """Get a Chromecast by friendly name."""
    if friendly_name in _chromecasts:
        return _chromecasts[friendly_name]

    # Try rediscovering if not found
    discover_chromecasts()
    return _chromecasts.get(friendly_name)


def cast_url(friendly_name: str, url: str, force_launch: bool = True) -> bool:
    """Cast a URL to a Chromecast using DashCast.

    Args:
        friendly_name: The Chromecast's friendly name
        url: The URL to cast
        force_launch: Whether to force launch even if something is playing

    Returns:
        True if successful, False otherwise
    """
    try:
        cc = get_chromecast(friendly_name)
        if not cc:
            logger.error(f"Chromecast '{friendly_name}' not found")
            return False

        # Wait for device to be ready
        cc.wait()

        # Use DashCast to display URL
        # DashCast app ID: B95BBCFB
        from pychromecast.controllers.dashcast import DashCastController

        dashcast = DashCastController()
        cc.register_handler(dashcast)

        # Load the URL
        dashcast.load_url(url, force=force_launch)
        logger.info(f"Cast URL {url} to {friendly_name} via DashCast")
        return True

    except Exception as e:
        logger.error(f"Cast error: {e}")
        return False


def stop_chromecasts():
    """Stop the discovery browser."""
    global _browser
    if _browser:
        _browser.stop_discovery()
        _browser = None
