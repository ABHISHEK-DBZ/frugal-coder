from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api import auth, projects, sessions, approvals, analytics, research
from app.events.hub import event_hub

# Initialize database tables on startup
init_db()

app = FastAPI(
    title="Frugal Coder API",
    description="The Budget-Aware, Privacy-First AI Coding Agent REST API",
    version="1.0.0",
    docs_url=f"{settings.API_V1_STR}/docs",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(sessions.router, prefix=settings.API_V1_STR)
app.include_router(approvals.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(research.router, prefix=settings.API_V1_STR)

@app.websocket("/ws/sessions/{session_id}")
@app.websocket("/api/v1/events/{session_id}")
async def websocket_session_events(websocket: WebSocket, session_id: str):
    """Live execution event stream for the coding workspace."""
    await event_hub.connect(session_id, websocket)
    try:
        while True:
            # Keep connection alive and accept incoming pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        event_hub.disconnect(session_id, websocket)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "frugal-coder-backend",
        "version": "1.0.0"
    }

