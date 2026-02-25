"""
Configuración centralizada del proyecto Moltbot.

Todas las variables de entorno se leen aquí. Los módulos del proyecto
importan las constantes desde este fichero en lugar de leer os.getenv directamente.
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass, field


def _require_env(name: str) -> str:
    """Devuelve el valor de una variable de entorno obligatoria o aborta el arranque."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"La variable de entorno '{name}' es obligatoria y no está definida."
        ) 
    return value


@dataclass(frozen=True)
class RabbitMQConfig:
    """Configuración de conexión a RabbitMQ."""

    user: str = os.getenv("RABBIT_USER", "guest")
    password: str = os.getenv("RABBIT_PASSWORD", "guest")
    host: str = os.getenv("RABBIT_HOST", "rabbitmq")
    queue_comandos: str = "comandos_bot"
    queue_facturas: str = "tareas_facturas"
    queue_respuestas: str = "respuestas_bot"


@dataclass(frozen=True)
class PostgresConfig:
    """Configuración de conexión a PostgreSQL."""

    host: str = os.getenv("POSTGRES_HOST", "postgres")
    database: str = os.getenv("POSTGRES_DB", "n8n")
    user: str = os.getenv("POSTGRES_USER", "n8n_user")
    password: str = os.getenv("POSTGRES_PASSWORD", "n8n_password")


@dataclass(frozen=True)
class DiscordConfig:
    """Configuración de integración con Discord."""

    webhook_url_facturas: str = os.getenv("DISCORD_WEBHOOK_URL_FACTURAS", "")
    request_timeout: int = int(os.getenv("DISCORD_REQUEST_TIMEOUT", "10"))


@dataclass(frozen=True)
class BackupConfig:
    """Configuración de backups."""

    output_folder: str = os.getenv("BACKUP_OUTPUT_FOLDER", "/n8n-workflows")


@dataclass(frozen=True)
class AppConfig:
    """Configuración raíz que agrupa todas las secciones."""

    rabbitmq: RabbitMQConfig = field(default_factory=RabbitMQConfig)
    postgres: PostgresConfig = field(default_factory=PostgresConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


# --- Instancia global de configuración ---
settings = AppConfig()


def setup_logging() -> None:
    """Configura el logging del proyecto según LOG_LEVEL."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
