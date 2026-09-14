import pytest
from main import app
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():               
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("main.conectar_banco")
def test_listar_imoveis_vazio(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value= mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM tabela_imoveis"
    )
    mock_cursor.fetchall.assert_only_called_once()
    mock_cursor.close.assert_only_called_once()
    mock_conn.close.assert_only_called_once()


@patch("main.conectar_banco")
def test_listar_imoveis(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
    (1,"Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"),
    (2,'Price Prairie', 'Travessa', 'Colonton', 'North Garyville', '93354', 'casa em condominio', 260069.89, '2021-11-30'),
    (3,'Taylor Ranch', 'Avenida', 'West Jennashire', 'Katherinefurt', '51116', 'apartamento', 815969.92, '2020-04-24'),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"},
        {"id": 2, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville", "cep": "93354", "tipo": "casa em condominio", "valor": 260069.89, "data_aquisicao": "2021-11-30"},
        {"id": 3, "logradouro": "Taylor Ranch", "tipo_logradouro": "Avenida", "bairro": "West Jennashire", "cidade": "Katherinefurt", "cep": "51116", "tipo": "apartamento", "valor": 815969.92, "data_aquisicao": "2020-04-24"}
    ]

    mock_cursor.execute.assert_only_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM tabela_imoveis"
    )
    mock_cursor.fetchall.assert_only_called_once()
    mock_cursor.close.assert_only_called_once()
    mock_conn.close.assert_only_called_once()


@patch("main.conectar_banco"}
def test_listar_imovel_id_}k(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_listar_imoveis_id_erro(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_adicionar_imovel_ok(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_adicionar_imovel_erro(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_atualizar_imovel_ok(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_atualizar_imovel_erro(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_remover_imovel_ok(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_remover_imovel_erro(mock_conectar_banco,client):
    ###
    
@patch("main.conectar_banco")
def test_listar_imovel_tipo_ok(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_listar_imovel_tipo_erro(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_listar_imovel_cidade_ok(mock_conectar_banco,client):
    ###

@patch("main.conectar_banco")
def test_listar_imovel_cidade_erro(mock_conectar_banco,client):
    ###