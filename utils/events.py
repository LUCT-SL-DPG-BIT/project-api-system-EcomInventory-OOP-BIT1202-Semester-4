"""
utils/events.py — Server-Sent Events broadcast hub.

Any router that modifies data calls notify(event_type).
All connected browser clients receive the event and silently
refresh the relevant section without the user having to reload.
"""
import asyncio
from typing import AsyncGenerator

# One asyncio.Queue per connected browser tab
_clients: set[asyncio.Queue] = set()


def notify(event_type: str) -> None:
    """Broadcast a named event to every connected SSE client."""
    msg = f"data: {event_type}\n\n"
    for queue in list(_clients):
        try:
            queue.put_nowait(msg)
        except asyncio.QueueFull:
            pass


async def event_stream(request) -> AsyncGenerator[str, None]:
    """
    Async generator that keeps a long-lived HTTP connection open and
    yields SSE messages.  A heartbeat comment is sent every 20 s so
    the browser does not time out the connection.
    """
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    _clients.add(queue)
    try:
        yield ": connected\n\n"           # immediate confirmation
        while True:
            if await request.is_disconnected():
                break
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=20)
                yield msg
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"   # keep-alive
    finally:
        _clients.discard(queue)
