from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from codetrace.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CodeTrace API",
        description="Algorithm visualization and local Python solution evaluation",
        version="0.1.0",
    )
    origins = os.environ.get("CODETRACE_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")
    return app


app = create_app()
