from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.infra.repositories import ScenarioRepository


def _scenario_dirs() -> list[Path]:
    env_dir = os.getenv("HANSE_SCENARIO_DIR")
    candidates: list[Path] = []
    if env_dir:
        candidates.append(Path(env_dir))

    # Local development layouts.
    candidates.append(Path(__file__).resolve().parents[3] / "data" / "scenarios")
    candidates.append(Path(__file__).resolve().parents[4] / "data" / "scenarios")

    # PyInstaller-style runtime.
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "data" / "scenarios")

    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def load_seed_scenarios(session: Session) -> None:
    repo = ScenarioRepository(session)
    seen_ids: set[str] = set()
    for scenario_dir in _scenario_dirs():
        if not scenario_dir.exists():
            continue
        for scenario_file in scenario_dir.glob("*.json"):
            payload = json.loads(scenario_file.read_text(encoding="utf-8"))
            scenario_id = payload["id"]
            if scenario_id in seen_ids:
                continue
            seen_ids.add(scenario_id)
            repo.upsert(
                scenario_id=scenario_id,
                name=payload["name"],
                version=payload.get("version", "1.0.0"),
                payload=payload,
            )
