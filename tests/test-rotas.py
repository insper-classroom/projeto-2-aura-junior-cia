import pytest
from unittest.mock import patch, MagicMock
from servidor import app


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("servidor.conectar_banco")
def test_listar_imoveis_vazio(mock_conectar_banco, client):
    """GET /imoveis - retorna lista vazia."""
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value   = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []
    mock_conn.cursor.assert_called_once_with(dictionary=True)
    mock_cursor.execute.assert_called_once_with(
        "SELECT id, logradouro, tipo_logradouro, bairro, cidade, "
        "cep, tipo, valor, data_aquisicao FROM imoveis"
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("servidor.conectar_banco")
def test_listar_imoveis_com_dados(mock_conectar_banco, client):
    """GET /imoveis - retorna lista com itens."""
    imovel = {
        "id": 1, "logradouro": "Rua A", "tipo_logradouro": "Rua",
        "bairro": "Centro", "cidade": "SP", "cep": "01001-000",
        "tipo": "apartamento", "valor": 300000.0, "data_aquisicao": "2023-01-01",
    }
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchall.return_value = [imovel]
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == [imovel]

@patch("servidor.conectar_banco")
def test_pegar_um_imovel(mock_conectar_banco, client):
    """GET /imoveis - retorna lista com itens."""
    imovel = {
        "id": 1, "logradouro": "Rua A", "tipo_logradouro": "Rua",
        "bairro": "Centro", "cidade": "SP", "cep": "01001-000",
        "tipo": "apartamento", "valor": 300000.0, "data_aquisicao": "2023-01-01",
    }
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchone.return_value = imovel
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == imovel

