"""Tests de la capa de acceso a datos (db/engine.py) con cursor mockeado."""

from __future__ import annotations

from unittest.mock import MagicMock, call

import psycopg2
import pytest

from moltbot.db.engine import (
    get_n8n_execution_count,
    get_total_gastos_mes,
    get_workflows,
    insert_factura,
    setup_db,
)


# ---------------------------------------------------------------------------
# Helper: obtener el cursor mock desde mock_db_connection
# ---------------------------------------------------------------------------
# El código fuente usa ``with conn.cursor() as cur``, por lo que el cursor
# real es ``mock_conn.cursor().__enter__()``.

def _cursor(mock_conn: MagicMock) -> MagicMock:
    """Devuelve el mock del cursor que ven las funciones bajo test."""
    return mock_conn.cursor().__enter__()


# ======================================================================
# setup_db
# ======================================================================

class TestSetupDb:
    """Verifica que ``setup_db`` ejecuta las queries DDL esperadas."""

    def test_ejecuta_tres_queries(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.reset_mock()

        setup_db()

        assert cur.execute.call_count == 3

    def test_crea_schema_moltbot(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.reset_mock()

        setup_db()

        primera_query = cur.execute.call_args_list[0][0][0]
        assert "CREATE SCHEMA" in primera_query
        assert "moltbot" in primera_query

    def test_crea_tabla_facturas(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.reset_mock()

        setup_db()

        segunda_query = cur.execute.call_args_list[1][0][0]
        assert "facturas_gastos" in segunda_query

    def test_crea_tabla_logs(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.reset_mock()

        setup_db()

        tercera_query = cur.execute.call_args_list[2][0][0]
        assert "logs_infraestructura" in tercera_query

    def test_hace_commit(self, mock_db_connection: MagicMock) -> None:
        setup_db()
        mock_db_connection.commit.assert_called()

    def test_error_db_no_propaga(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.side_effect = psycopg2.Error("connection refused")

        setup_db()  # no debe lanzar excepción


# ======================================================================
# insert_factura
# ======================================================================

class TestInsertFactura:
    """Tests de ``insert_factura``."""

    def test_devuelve_id(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (42,)

        result = insert_factura("iberdrola", 95.23, "texto factura")

        assert result == 42

    def test_query_contiene_parametros(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (1,)

        insert_factura("o2", 38.90, "detalle")

        args = cur.execute.call_args[0]
        query = args[0]
        params = args[1]
        assert "INSERT INTO" in query
        assert "facturas_gastos" in query
        assert params[0] == "o2"
        assert params[1] == pytest.approx(38.90)
        assert params[2] == "detalle"

    def test_hace_commit(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (1,)

        insert_factura("test", 10.0)

        mock_db_connection.commit.assert_called()

    def test_error_db_devuelve_none(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.side_effect = psycopg2.Error("insert failed")

        result = insert_factura("test", 10.0)

        assert result is None

    def test_importe_con_coma_se_limpia(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (5,)

        insert_factura("test", "95,50")  # type: ignore[arg-type]

        params = cur.execute.call_args[0][1]
        assert params[1] == pytest.approx(95.50)

    def test_texto_por_defecto_vacio(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (1,)

        insert_factura("test", 10.0)

        params = cur.execute.call_args[0][1]
        assert params[2] == ""


# ======================================================================
# get_total_gastos_mes
# ======================================================================

class TestGetTotalGastosMes:
    """Tests de ``get_total_gastos_mes``."""

    def test_devuelve_total(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (350.75,)

        result = get_total_gastos_mes()

        assert result == pytest.approx(350.75)

    def test_sin_facturas_devuelve_cero(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (0,)

        result = get_total_gastos_mes()

        assert result == pytest.approx(0.0)

    def test_devuelve_float(self, mock_db_connection: MagicMock) -> None:
        from decimal import Decimal

        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (Decimal("123.45"),)

        result = get_total_gastos_mes()

        assert isinstance(result, float)
        assert result == pytest.approx(123.45)

    def test_error_db_devuelve_none(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.side_effect = psycopg2.Error("query failed")

        result = get_total_gastos_mes()

        assert result is None


# ======================================================================
# get_n8n_execution_count
# ======================================================================

class TestGetN8nExecutionCount:
    """Tests de ``get_n8n_execution_count``."""

    def test_devuelve_conteo(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (128,)

        result = get_n8n_execution_count()

        assert result == 128

    def test_cero_ejecuciones(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (0,)

        result = get_n8n_execution_count()

        assert result == 0

    def test_query_contiene_execution_entity(
        self, mock_db_connection: MagicMock,
    ) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchone.return_value = (0,)

        get_n8n_execution_count()

        query = cur.execute.call_args[0][0]
        assert "execution_entity" in query

    def test_error_db_devuelve_none(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.side_effect = psycopg2.Error("table not found")

        result = get_n8n_execution_count()

        assert result is None


# ======================================================================
# get_workflows
# ======================================================================

class TestGetWorkflows:
    """Tests de ``get_workflows``."""

    def test_devuelve_lista_de_tuples(self, mock_db_connection: MagicMock) -> None:
        expected = [
            ("Workflow A", '["n1"]', '{"c":1}'),
            ("Workflow B", '["n2"]', '{"c":2}'),
        ]
        cur = _cursor(mock_db_connection)
        cur.fetchall.return_value = expected

        result = get_workflows()

        assert result == expected

    def test_lista_vacia(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchall.return_value = []

        result = get_workflows()

        assert result == []

    def test_query_contiene_workflow_entity(
        self, mock_db_connection: MagicMock,
    ) -> None:
        cur = _cursor(mock_db_connection)
        cur.fetchall.return_value = []

        get_workflows()

        query = cur.execute.call_args[0][0]
        assert "workflow_entity" in query

    def test_error_db_devuelve_none(self, mock_db_connection: MagicMock) -> None:
        cur = _cursor(mock_db_connection)
        cur.execute.side_effect = psycopg2.Error("connection lost")

        result = get_workflows()

        assert result is None
