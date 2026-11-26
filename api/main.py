import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api.routers import auth, clinical, pdf

app = FastAPI(
    title="PSIQUE Clinical API",
    description="Backend REST en Python/FastAPI para el Sistema de Gestión Clínico Psicológica PSIQUE",
    version="1.1.0",
)

allowed_origins = [
    o.strip()
    for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clinical.router)
app.include_router(pdf.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "psique-api"}
