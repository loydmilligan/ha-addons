#!/usr/bin/env python3
"""Lyric Scroll - Main entry point."""

import asyncio
import logging
import os
import signal
from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# WebSocket clients
clients: set[web.WebSocketResponse] = set()


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    """Handle WebSocket connections from frontend."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    clients.add(ws)
    logger.info(f"Client connected. Total clients: {len(clients)}")

    try:
        # Send initial idle state
        await ws.send_json({"type": "idle"})

        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = msg.json()
                logger.info(f"Received from client: {data}")
                # Handle client messages (settings, resync requests)
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"WebSocket error: {ws.exception()}")
    finally:
        clients.discard(ws)
        logger.info(f"Client disconnected. Total clients: {len(clients)}")

    return ws


async def broadcast(message: dict) -> None:
    """Broadcast message to all connected clients."""
    if not clients:
        return

    for client in list(clients):
        try:
            await client.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
            clients.discard(client)


async def index_handler(request: web.Request) -> web.FileResponse:
    """Serve the main HTML page."""
    return web.FileResponse('/frontend/index.html')


def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application()

    # Routes
    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/css', '/frontend/css')
    app.router.add_static('/js', '/frontend/js')

    return app


async def main() -> None:
    """Main entry point."""
    logger.info("Lyric Scroll starting...")

    # Get ingress port from environment
    port = int(os.environ.get('INGRESS_PORT', 8099))

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    logger.info(f"Server started on port {port}")

    # Wait for shutdown signal
    stop_event = asyncio.Event()

    def handle_signal():
        logger.info("Shutdown signal received")
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, handle_signal)

    await stop_event.wait()

    logger.info("Shutting down...")
    await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
