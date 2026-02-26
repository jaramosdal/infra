# Copilot instructions for `infra` / `moltbot`

## Big picture architecture
- This repo is Docker-first: `docker-compose.yml` orchestrates `postgres`, `rabbitmq`, `n8n`, and `moltbot`.
- `moltbot` is a long-running RabbitMQ consumer (`moltbot/src/moltbot/app.py`) that handles:
  - command messages from queue `comandos_bot`
  - invoice OCR/text messages from queue `tareas_facturas`
- `moltbot` writes business data to Postgres (`moltbot/src/moltbot/db/engine.py`) and sends notifications to Discord webhook (`moltbot/src/moltbot/utils/discord_bot.py`).
- `moltbot` also reads n8n tables directly (`execution_entity`, `workflow_entity`) for status and workflow backup commands.

## Runtime and developer workflow
- Rebuild/restart after code changes with `docker-compose up -d --build` (project README convention).
- Follow bot runtime logs with `docker logs -f moltbot_app`.
- Python package metadata and deps are in `moltbot/pyproject.toml` (`pika`, `psycopg2-binary`, `requests`; dev: `pytest`, `ruff`).
- Container entrypoint is `python -u -m moltbot` (`moltbot/Dockerfile`), so `moltbot/__main__.py` and `moltbot/app.py` are critical startup files.

## Project-specific coding patterns
- Keep configuration centralized in `moltbot/src/moltbot/config/settings.py`; do not scatter new `os.getenv` calls across modules.
- Use import-side registration for extensibility:
  - Commands: `@register_command(...)` in `moltbot/src/moltbot/commands/*.py`; loaded by importing `moltbot.commands`.
  - Bill parsers: `@register_parser(...)` in `moltbot/src/moltbot/processors/bill_parser.py`.
- When adding a new command, return a user-facing string (dispatcher contract in `commands/base.py`).
- Rabbit handlers (`messaging/rabbit.py`) currently use `auto_ack=True`; failures are logged, not retried. Keep behavior consistent unless explicitly changing delivery semantics.
- DB access pattern is function-based with short-lived connections via `_get_connection()` context manager (`db/engine.py`), not ORM models.

## Integration boundaries
- RabbitMQ queue names are defined in `RabbitMQConfig` (`settings.py`), not hardcoded in random modules.
- Postgres schema for bot-owned tables is `moltbot` (`setup_db()` creates `moltbot.facturas_gastos` and `moltbot.logs_infraestructura`).
- n8n data assumptions are hard dependencies:
  - `get_n8n_execution_count()` queries `execution_entity`
  - `get_workflows()` queries `workflow_entity`
- Backup output defaults to `/n8n-workflows` in container (`BackupConfig.output_folder`), mapped from host `./n8n-workflows` in compose.

## Change guidance for AI agents
- Prefer minimal, surgical edits in existing modules over introducing new layers.
- Match current code style: Spanish log/messages, typed functions, straightforward procedural flow.
- Preserve startup side effects in `app.py`:
  - `setup_logging()` and `setup_db()` run before Rabbit connection.
  - `import moltbot.commands as _commands` is intentional for command auto-registration.
- Validate by checking container logs and (if added) targeted tests under `moltbot/tests`; current test tree is mostly scaffolding.