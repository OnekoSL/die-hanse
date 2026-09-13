from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.infra.db import SessionLocal, init_db
from app.infra.seeds import load_seed_scenarios


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as session:
        load_seed_scenarios(session)
        session.commit()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Die Hanse API", version="0.1.0", lifespan=lifespan)
    allowed_origins = os.getenv(
        "HANSE_ALLOWED_ORIGINS",
        ",".join(
            [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:1420",
                "http://127.0.0.1:1420",
                "http://tauri.localhost",
                "tauri://localhost",
            ]
        ),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in allowed_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)

    return app


app = create_app()
