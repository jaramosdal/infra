"""Módulo de backup de workflows de n8n."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

from moltbot.config import settings
from moltbot.db import get_workflows

logger = logging.getLogger(__name__)

_SAFE_FILENAME_RE = re.compile(r"[^\w\s_-]", re.UNICODE)


def _sanitize_filename(name: str) -> str:
    """Convierte un nombre arbitrario en un nombre de fichero seguro."""
    sanitized = _SAFE_FILENAME_RE.sub("", name)
    return sanitized.strip().replace(" ", "_") or "unnamed_workflow"


def backup_n8n_workflows(output_folder: str | None = None) -> Optional[int]:
    """
    Lee los flujos de la tabla de n8n y los guarda como archivos ``.json``.

    Returns:
        Número de workflows exportados, o ``None`` en caso de error.
    """
    folder = Path(output_folder or settings.backup.output_folder)
    folder.mkdir(parents=True, exist_ok=True)

    try:
        workflows = get_workflows()
        if not workflows:
            logger.warning("No se encontraron workflows para exportar.")
            return 0

        for name, nodes, connections in workflows:
            filepath = folder / f"{_sanitize_filename(name)}.json"
            workflow_data = {
                "name": name,
                "nodes": nodes,
                "connections": connections,
            }
            filepath.write_text(
                json.dumps(workflow_data, indent=4, ensure_ascii=False),
                encoding="utf-8",
            )

        total = len(workflows)
        logger.info("Backup completado: %d workflows exportados a %s", total, folder)
        return total

    except Exception:
        logger.exception("Error en backup de workflows.")
        return None
