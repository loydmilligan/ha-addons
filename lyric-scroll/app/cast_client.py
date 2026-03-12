"""Direct Chromecast control using pychromecast."""

import logging
from typing import Optional
import pychromecast
from pychromecast.controllers.dashcast import DashCastController

logger = logging.getLogger(__name__)

# Cache of connected chromecasts by IP
_chromecasts: dict = {}


def get_chromecast_by_ip(ip_address: str, port: int = 8009) -> Optional[pychromecast.Chromecast]:
    """Get or create a Chromecast connection by IP address."""
    if ip_address in _chromecasts:
        cc = _chromecasts[ip_address]
        # Check if still connected
        if cc.socket_client and cc.socket_client.is_connected:
            return cc

    try:
        logger.info(f"Connecting to Chromecast at {ip_address}:{port}...")

        # Connect directly by IP - try different API approaches
        try:
            # Newer pychromecast API
            from pychromecast.discovery import CastBrowser, SimpleCastListener
            import zeroconf

            zconf = zeroconf.Zeroconf()
            cast_info = pychromecast.models.CastInfo(
                services=set(),
                uuid=None,
                model_name="Chromecast",
                friendly_name="Chromecast",
                host=ip_address,
                port=port,
                cast_type="cast",
                manufacturer="Google"
            )
            cc = pychromecast.get_chromecast_from_cast_info(cast_info, zconf)
        except Exception as e1:
            logger.debug(f"New API failed ({e1}), trying legacy...")
            # Legacy pychromecast API - positional argument
            cc = pychromecast.Chromecast(ip_address)

        cc.wait()
        _chromecasts[ip_address] = cc
        logger.info(f"Connected to Chromecast: {cc.cast_info.friendly_name if hasattr(cc, 'cast_info') else ip_address}")
        return cc

    except Exception as e:
        logger.error(f"Error connecting to Chromecast at {ip_address}: {e}")
        return None


def cast_url_to_ip(ip_address: str, url: str, force_launch: bool = True) -> bool:
    """Cast a URL to a Chromecast using DashCast.

    Args:
        ip_address: The Chromecast's IP address
        url: The URL to cast
        force_launch: Whether to force launch even if something is playing

    Returns:
        True if successful, False otherwise
    """
    try:
        cc = get_chromecast_by_ip(ip_address)
        if not cc:
            return False

        # Use DashCast to display URL
        dashcast = DashCastController()
        cc.register_handler(dashcast)

        # Load the URL
        logger.info(f"Casting {url} to {cc.cast_info.friendly_name} via DashCast")
        dashcast.load_url(url, force=force_launch)
        return True

    except Exception as e:
        logger.error(f"Cast error: {e}")
        return False


def disconnect_all():
    """Disconnect all cached Chromecast connections."""
    for ip, cc in _chromecasts.items():
        try:
            cc.disconnect()
        except:
            pass
    _chromecasts.clear()
