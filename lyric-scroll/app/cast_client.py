"""Direct Chromecast control using pychromecast."""

import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import pychromecast
from pychromecast.controllers.dashcast import DashCastController

logger = logging.getLogger(__name__)

# Cache of connected chromecasts by IP
_chromecasts: dict = {}
_executor = ThreadPoolExecutor(max_workers=2)

# Connection timeout in seconds
CONNECT_TIMEOUT = 10


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

        # Wait with timeout
        logger.info(f"Waiting for Chromecast connection (timeout={CONNECT_TIMEOUT}s)...")
        cc.wait(timeout=CONNECT_TIMEOUT)

        if not cc.socket_client or not cc.socket_client.is_connected:
            logger.error(f"Chromecast at {ip_address} did not connect in time")
            return None

        _chromecasts[ip_address] = cc
        friendly = cc.cast_info.friendly_name if hasattr(cc, 'cast_info') and cc.cast_info else ip_address
        logger.info(f"Connected to Chromecast: {friendly}")
        return cc

    except Exception as e:
        logger.error(f"Error connecting to Chromecast at {ip_address}: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
