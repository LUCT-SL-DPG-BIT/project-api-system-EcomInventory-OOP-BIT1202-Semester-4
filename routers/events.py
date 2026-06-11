from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from utils.events import event_stream

router = APIRouter(tags=["Real-time"])


@router.get("/api/v1/events", include_in_schema=False)
async def sse_endpoint(request: Request):
    """
    Server-Sent Events stream.
    Browsers connect here after login and receive push notifications
    whenever inventory data changes (products, categories).
    """
    return StreamingResponse(
        event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":    "keep-alive",
        },
    )
