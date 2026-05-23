"""
Network Support Ticket Dashboard — Main Application
Production-grade FastAPI service
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

load_dotenv()

from backend.database import init_db
from backend.routes import router as ticket_router

# ─── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ticket_dashboard")


# ─── Lifespan ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Network Support Ticket Dashboard...")
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    yield
    logger.info("🛑 Shutting down service...")


# ─── App Instance ──────────────────────────────────────────────────
app = FastAPI(
    title="Network Support Ticket Dashboard",
    description="Production-grade support ticket management system with full CRUD, status tracking, and real-time dashboard statistics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─── CORS ─────────────────────────────────────────────────────────
cors_origins_raw = os.getenv("CORS_ORIGINS", "*")
cors_origins = [o.strip() for o in cors_origins_raw.split(",")] if cors_origins_raw != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# ─── Exception Handlers ────────────────────────────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": str(exc.detail), "status_code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"])
        errors.append(f"{field}: {err['msg']}")
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "errors": errors},
    )


# ─── Routes ────────────────────────────────────────────────────────
app.include_router(ticket_router)

# Serve static frontend files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# ─── Health & Root ─────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "Network Support Ticket Dashboard", "version": "1.0.0"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend():
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info",
        workers=1,
    )
