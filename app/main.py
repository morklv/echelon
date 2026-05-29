from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import models
from app.database import engine
from app.routers import auth, incidents, infrastructure, infrastucture_dependencies
from app.services import websocket_service


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ECHELON API")


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)



origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://echelon-frontend-seven.vercel.app",
    "https://github.com/morklv/echelon-frontend",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(infrastructure.router)
app.include_router(infrastucture_dependencies.router)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "app": "ECHELON"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_service.connect_client(websocket)

    try:
        while True:
            await websocket.receive_text()

    except Exception:
        await websocket_service.disconnect_client(websocket)