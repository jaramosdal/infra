#!/bin/bash
# Crea la base de datos de GlitchTip si no existe.
# Se ejecuta automáticamente por Postgres al inicializar el volumen de datos.
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
    SELECT 'CREATE DATABASE glitchtip OWNER '"$POSTGRES_USER"
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'glitchtip')\gexec
EOSQL
