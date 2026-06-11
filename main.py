from pathlib import Path
from dotenv import load_dotenv
import time, os, sys

# Enable ANSI colour codes in Windows console (no-op on Mac/Linux)
if sys.platform == 'win32':
    os.system('')

# Load .env FIRST — before any local module reads os.getenv()
load_dotenv(override=True)

# Strip stray whitespace/newlines that sneak in when values are
# copy-pasted into hosting dashboards (e.g. Render env vars)
for _key in ("DATABASE_URL", "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
             "SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD",
             "APP_URL", "ADMIN_EMAIL", "LOW_STOCK_THRESHOLD"):
    if os.environ.get(_key):
        os.environ[_key] = os.environ[_key].strip()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).parent

from database import engine, Base
from routers import users, products, categories, orders, stats, analytics, vouchers, reviews, events

# ─────────────────────────────────────────────
# TERMINAL COLOUR CODES
# ─────────────────────────────────────────────
_C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "cyan":   "\033[96m",
    "grey":   "\033[90m",
    "blue":   "\033[94m",
}

# ─────────────────────────────────────────────
# CREATE ALL TABLES
# ─────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────
# APP INITIALIZATION
# ─────────────────────────────────────────────
app = FastAPI(
    title="E-Commerce Inventory API",
    description="""
## E-Commerce Inventory API 🛒

A **FastAPI-based REST API** for managing an e-commerce inventory system.

### Features
- 🔐 JWT Authentication & Role-Based Authorization
- 📦 Product & Category Management
- 🛍️ Order Processing with Stock Management
- 🗄️ PostgreSQL Database via SQLAlchemy ORM
- ⚡ Async Programming Support
- 📄 Full Swagger UI & ReDoc Documentation

### SDG Alignment
This API supports **SDG 8 – Decent Work and Economic Growth** by empowering
local Sierra Leonean businesses and traders to manage their inventory and
reach customers digitally.

### Groups
**Group D** — PROG315 Object-Oriented Programming 2  
Limkokwing University of Creative Technology, Sierra Leone  
Semester 4, March–July 2026
    """,
    version="1.0.0",
    contact={
        "name": "Group D",
        "email": "amandus.bcoker@limkokwing.edu.sl",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────
# REQUEST LOGGING MIDDLEWARE
# Pure ASGI class — no body buffering, no deadlock.
# BaseHTTPMiddleware buffers FileResponse bodies
# which deadlocks large HTML files. This streams
# responses through untouched and logs after.
# ─────────────────────────────────────────────
class _RequestLogger:
    def __init__(self, app):
        self._app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        path   = scope.get("path", "")
        method = scope.get("method", "GET")

        if path.startswith("/static") or path in ("/", "/favicon.ico"):
            await self._app(scope, receive, send)
            return

        t0     = time.perf_counter()
        status = [200]

        async def _send_wrap(message):
            if message["type"] == "http.response.start":
                status[0] = message.get("status", 200)
            await send(message)

        await self._app(scope, receive, _send_wrap)
        ms = (time.perf_counter() - t0) * 1000

        s  = status[0]
        c  = _C["green"] if s < 300 else (_C["yellow"] if s < 500 else _C["red"])
        mc = {"GET": _C["cyan"], "POST": _C["green"], "PATCH": _C["yellow"],
              "PUT": _C["yellow"], "DELETE": _C["red"]}.get(method, _C["blue"])

        print(
            f"{_C['grey']}  >> {mc}{_C['bold']}{method:<7}{_C['reset']} "
            f"{path:<45} "
            f"{c}{_C['bold']}{s}{_C['reset']} "
            f"{_C['grey']}({ms:.0f}ms){_C['reset']}"
        )


# ─────────────────────────────────────────────
# CORS MIDDLEWARE
# ─────────────────────────────────────────────
app.add_middleware(_RequestLogger)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# INCLUDE ROUTERS
# ─────────────────────────────────────────────
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(stats.router)
app.include_router(analytics.router)
app.include_router(vouchers.router)
app.include_router(reviews.router)
app.include_router(events.router)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# ─────────────────────────────────────────────
# ROOT ENDPOINT
# ─────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api", tags=["Root"])
def api_info():
    return {
        "message": "Welcome to the E-Commerce Inventory API",
        "dashboard": "/",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
        "group": "Group D — PROG315",
        "sdg": "SDG 8 – Decent Work and Economic Growth",
    }


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "healthy", "api": "E-Commerce Inventory API"}
