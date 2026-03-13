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

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 200
    assert response.get_json() == [imovel]

@patch("servidor.conectar_banco")
def test_pegar_um_imovel(mock_conectar_banco, client):
    """GET /imoveis/<id> - retorna um imóvel com base no id."""
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

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 200
    assert response.get_json() == imovel

@patch("servidor.conectar_banco")
def test_pegar_um_imovel_nao_encontrado(mock_conectar_banco, client):
    """GET /imoveis/<id> - nao retorna um imóvel com base no id."""
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis/1")

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 404
    assert response.get_json() == {"error": "Imóvel não encontrado"}

@patch("servidor.conectar_banco")
def test_criar_imovel(mock_conectar_banco, client):
    """POST /imoveis/add - adiciona um imóvel com base no id."""
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_conectar_banco.return_value  = mock_conn

    response = client.post("/imoveis/add", json={
        "logradouro": "Rua A",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "SP",
        "cep": "01001-000",
        "tipo": "apartamento",
        "valor": 300000.0,
        "data_aquisicao": "2023-01-01"
    })
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (?, ?, ?, ?, ?, ?, ?, ?,)",
        ("Rua A", "Rua", "Centro", "SP", "01001-000", "apartamento",300000.0, "2023-01-01"),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 201
    assert response.get_json() == {"message": "Imóvel adicionado com sucesso"}


@patch("servidor.conectar_banco")
def test_criar_imovel_erro_validacao(mock_conectar_banco, client):
    """POST /imoveis/add - falta campo obrigatório -> 400. Não deve acessar o banco."""
    response = client.post("/imoveis/add", json={"logradouro": "saulo"})

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()

@patch("servidor.conectar_banco")
def test_atualizar_imovel_ok(mock_conectar_banco, client):
    """PUT /imoveis/<id> - atualiza com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Rua A",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "SP",
        "cep": "01001-000",
        "tipo": "apartamento",
        "valor": 300000.0,
        "data_aquisicao": "2023-01-01"
    }
    response = client.put("/imoveis/1", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel atualizado com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = ?, tipo_logradouro = ?, bairro = ?, cidade = ?, cep = ?, tipo = ?, valor = ?, data_aquisicao = ? WHERE id = ?",
        ("Rua A", "Rua", "Centro", "SP", "01001-000", "apartamento", 300000.0, "2023-01-01", 1),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("servidor.conectar_banco")
def test_atualizar_imovel_not_found(mock_conectar_banco, client):
    """PUT /imoveis/<id> - imóvel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    payload = {
        "logradouro": "Rua A",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "SP",
        "cep": "01001-000",
        "tipo": "apartamento",
        "valor": 300000.0,
        "data_aquisicao": "2023-01-01"
    }
    response = client.put("/imoveis/1", json=payload)

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = ?, tipo_logradouro = ?, bairro = ?, cidade = ?, cep = ?, tipo = ?, valor = ?, data_aquisicao = ? WHERE id = ?",
        ("Rua A", "Rua", "Centro", "SP", "01001-000", "apartamento", 300000.0, "2023-01-01", 1),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("servidor.conectar_banco")
def test_deletar_imovel_ok(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - deleta com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "Imóvel excluído com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = ?",
        (1,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()



@patch("servidor.conectar_banco") 
def test_deletar_imovel_not_found(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - imóvel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "Imóvel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = ?",
        (999,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
