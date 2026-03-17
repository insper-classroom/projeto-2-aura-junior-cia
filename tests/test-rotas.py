import pytest
from unittest.mock import patch, MagicMock
from servidor import app

SAMPLE_IMOVEL = {
    "bairro": "West Jennashire",
    "cep": "51116",
    "cidade": "Katherinefurt",
    "data_aquisicao": "2020-04-24",
    "id": 3,
    "logradouro": "Taylor Ranch",
    "tipo": "apartamento",
    "tipo_logradouro": "Avenida",
    "valor": 815970.0
}

SAMPLE_IMOVEL_2 = {
    "id": 1, "logradouro": "Rua A", "tipo_logradouro": "Rua",
    "bairro": "Centro", "cidade": "SP", "cep": "01001-000",
    "tipo": "apartamento", "valor": 300000.0, "data_aquisicao": "2023-01-01",
}


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


@patch("servidor.conectar_banco")
def test_listar_imoveis_com_dados(mock_conectar_banco, client):
    """GET /imoveis - retorna lista com itens."""
    imovel = SAMPLE_IMOVEL.copy()
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchall.return_value = [imovel]
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis")

    imovel["links"] = {
        "self": f"/imoveis/{imovel['id']}",
        "update": f"/imoveis/{imovel['id']}",
        "delete": f"/imoveis/{imovel['id']}"
    }
    assert response.status_code == 200
    assert response.get_json() == [imovel]

@patch("servidor.conectar_banco")
def test_pegar_um_imovel(mock_conectar_banco, client):
    """GET /imoveis/<id> - retorna um imóvel com base no id."""
    imovel = SAMPLE_IMOVEL_2.copy()
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchone.return_value = imovel
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis/1")

    imovel["links"] = {
        "self": "/imoveis/1",
        "update": "/imoveis/1",
        "delete": "/imoveis/1",
    }

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

    assert response.status_code == 404
    assert response.get_json() == {"error": "Imóvel não encontrado"}

@patch("servidor.conectar_banco")
def test_criar_imovel(mock_conectar_banco, client):
    """POST /imoveis/add - adiciona um imóvel com base no id."""
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchone.return_value = SAMPLE_IMOVEL.copy()
    mock_conectar_banco.return_value  = mock_conn

    response = client.post("/imoveis/add", json=SAMPLE_IMOVEL)
    expected_imovel = SAMPLE_IMOVEL.copy()
    expected_imovel["links"] = {
        "self": "/imoveis/3",
        "update": "/imoveis/3",
        "delete": "/imoveis/3",
    }

 

    assert response.status_code == 201
    assert response.get_json() == expected_imovel


@patch("servidor.conectar_banco")
def test_criar_imovel_erro_validacao(mock_conectar_banco, client):
    """POST /imoveis/add - falta campo obrigatório -> 400. Não deve acessar o banco."""
    response = client.post("/imoveis/add", json={"logradouro": "saulo"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Dados incompletos"}

    mock_conectar_banco.assert_not_called()

@patch("servidor.conectar_banco")
def test_atualizar_imovel_ok(mock_conectar_banco, client):
    """PUT /imoveis/<id> - atualiza com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_cursor.fetchone.return_value = SAMPLE_IMOVEL.copy()
    mock_conectar_banco.return_value = mock_conn

    payload = SAMPLE_IMOVEL.copy()
    response = client.put("/imoveis/1", json=payload)

    expected_imovel = SAMPLE_IMOVEL.copy()
    expected_imovel["id"] = 3
    expected_imovel["links"] = {
        "self": "/imoveis/3",
        "update": "/imoveis/3",
        "delete": "/imoveis/3",
    }

    assert response.status_code == 200
    assert response.get_json() == expected_imovel


@patch("servidor.conectar_banco")
def test_atualizar_imovel_not_found(mock_conectar_banco, client):
    """PUT /imoveis/<id> - imóvel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    payload =   SAMPLE_IMOVEL.copy()
    response = client.put("/imoveis/1", json=payload)


    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815970.0, "2020-04-24", 1),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 404
    assert response.get_json() == {"error": "Imóvel não encontrado"}

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
    assert response.get_json() == {
        "mensagem": "Imóvel deletado com sucesso!",
        "links": {"list": "/imoveis"},
    }


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
    assert response.get_json() == {"error": "Imóvel não encontrado"}

@patch("servidor.conectar_banco")
def test_listar_imoveis_filtrados_por_tipo(mock_conectar_banco, client):
    """GET /imoveis/search?tipo= - retorna lista com itens filtrados por tipo."""
    imovel = SAMPLE_IMOVEL.copy()
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchall.return_value = [imovel]
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis/search?tipo=apartamento")

    imovel["links"] = {
        "self": f"/imoveis/{imovel['id']}",
        "update": f"/imoveis/{imovel['id']}",
        "delete": f"/imoveis/{imovel['id']}",
    }

    assert response.status_code == 200
    assert response.get_json() == [imovel]

@patch("servidor.conectar_banco")
def test_listar_imoveis_filtrados_por_cidade(mock_conectar_banco, client):
    """GET /imoveis/search?cidade= - retorna lista com itens filtrados por cidade."""
    imovel = SAMPLE_IMOVEL.copy()
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchall.return_value = [imovel]
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis/search?cidade=SP")

    mock_cursor.execute.assert_called_once_with(
        "SELECT id, logradouro, tipo_logradouro, bairro, cidade, "
        "cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s",
        ("SP",),
    )

    imovel["links"] = {
        "self": f"/imoveis/{imovel['id']}",
        "update": f"/imoveis/{imovel['id']}",
        "delete": f"/imoveis/{imovel['id']}",
    }
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 200
    assert response.get_json() == [imovel]

@patch("servidor.conectar_banco")
def test_listar_imoveis_filtrados_por_tipo_(mock_conectar_banco, client):
    """GET /imoveis/search?tipo= - retorna lista com itens filtrados por tipo."""
    
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_cursor.fetchall.return_value = []
    mock_conectar_banco.return_value  = mock_conn

    response = client.get("/imoveis/search?tipo=apartamento")


    assert response.status_code == 404
    assert response.get_json() == {"message": "Nenhum imóvel encontrado"}

@patch("servidor.conectar_banco")
def test_listar_imoveis_filtrados_por_cidade_not_found(mock_conectar_banco, client):
    """GET /imoveis/search?cidade= - retorna lista com itens filtrados por cidade."""
    mock_conn   = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value     = mock_cursor
    mock_conectar_banco.return_value  = mock_conn
    mock_cursor.fetchall.return_value = []
    response = client.get("/imoveis/search?cidade=RJ")
    

    mock_cursor.execute.assert_called_once_with(
        "SELECT id, logradouro, tipo_logradouro, bairro, cidade, "
        "cep, tipo, valor, data_aquisicao FROM imoveis WHERE cidade = %s",
        ("RJ",),
    )


    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    assert response.status_code == 404
    assert response.get_json() == {"message": "Nenhum imóvel encontrado"}