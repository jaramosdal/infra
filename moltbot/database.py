import psycopg2
import os
from datetime import datetime

# Variables de entorno (ya las tienes)
POSTGRES_HOST = 'postgres'
POSTGRES_DB = os.getenv('POSTGRES_DB', 'n8n')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'n8n_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'n8n_password')

def get_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def setup_db():
    """Inicializa el esquema y todas las tablas del bot"""
    queries = [
        "CREATE SCHEMA IF NOT EXISTS moltbot;",
        # Tabla de Facturas
        """
        CREATE TABLE IF NOT EXISTS moltbot.facturas_gastos (
            id SERIAL PRIMARY KEY,
            proveedor VARCHAR(50) NOT NULL,
            importe DECIMAL(10, 2) NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            texto_original TEXT
        );
        """,
        # Tabla de Estado de Servicios (RabbitMQ, etc)
        """
        CREATE TABLE IF NOT EXISTS moltbot.logs_infraestructura (
            id SERIAL PRIMARY KEY,
            servicio VARCHAR(50) NOT NULL,
            estado VARCHAR(20) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for q in queries:
                    cur.execute(q)
                conn.commit()
                print("✅ Infraestructura 'moltbot' (facturas y servicios) lista.")
    except Exception as e:
        print(f"❌ Error en setup_db: {e}")

def insert_factura(proveedor, importe, texto=""):
    """Inserta una nueva factura en la base de datos"""
    query = """
    INSERT INTO moltbot.facturas_gastos (proveedor, importe, texto_original)
    VALUES (%s, %s, %s) RETURNING id;
    """
    try:
        # Limpiamos el importe: cambiamos comas por puntos si vienen del PDF
        importe_clean = float(str(importe).replace(',', '.'))
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (proveedor, importe_clean, texto))
                factura_id = cur.fetchone()[0]
                conn.commit()
                return factura_id
    except Exception as e:
        print(f"❌ Error al insertar factura: {e}")
        return None

def get_n8n_execution_count():
    """Tu consulta original de n8n"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM execution_entity;")
                return cur.fetchone()[0]
    except Exception as e:
        print(f"❌ Error DB: {e}")
        return "Error"