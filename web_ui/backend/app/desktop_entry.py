from __future__ import annotations

import os

import uvicorn
from app.main import app as fastapi_app


def main() -> None:
    host = os.getenv("HANSE_API_HOST", "127.0.0.1")
    port = int(os.getenv("HANSE_API_PORT", "18522"))
    uvicorn.run(fastapi_app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
