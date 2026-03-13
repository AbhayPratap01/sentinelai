from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from routes import analyze, threats, stats
from core.connection_manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SentinelAI backend starting...")
    yield
    print("SentinelAI backend shutting down...")

app = FastAPI(
    title="SentinelAI",
    description="Real-time LLM Prompt Injection & Jailbreak Detection",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(threats.router, prefix="/api", tags=["threats"])
app.include_router(stats.router, prefix="/api", tags=["stats"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {"status": "SentinelAI is running", "version": "1.0.0"}
