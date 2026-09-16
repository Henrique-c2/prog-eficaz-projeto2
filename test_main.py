import pytest
from main import app
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():               
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def links_imovel(id):
    return {
        "self": {"href": f"/imoveis/{id}", "method": "GET"},
        "atualizar": {"href": f"/imoveis/{id}", "method": "PUT"},
        "remover": {"href": f"/imoveis/{id}", "method": "DELETE"},
        "colecao": {"href": "/imoveis", "method": "GET"}
    }

def links_colecao():
    return {
        "self": {"href": "/imoveis", "method": "GET"},
        "criar": {"href": "/imoveis", "method": "POST"},
        "filtrar_por_tipo": {
            "href": "/imoveis?tipo={tipo}",
            "method": "GET",
            "templated": True
        },
        "filtrar_por_cidade": {
            "href": "/imoveis?cidade={cidade}",
            "method": "GET",
            "templated": True
        }
    }

def imovel_json(id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao):
    return {
        "id": id,
        "logradouro": logradouro,
        "tipo_logradouro": tipo_logradouro,
        "bairro": bairro,
        "cidade": cidade,
        "cep": cep,
        "tipo": tipo,
        "valor": valor,
        "data_aquisicao": data_aquisicao,
        "_links": links_imovel(id)
    }

@patch("main.conectar_banco")
def test_listar_imoveis_vazio(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value= mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == {
        "imoveis": [],
        "_links": links_colecao()
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis"
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

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
    assert response.get_json() == {
        "imoveis": [
            imovel_json(1, "Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"),
            imovel_json(2, "Price Prairie", "Travessa", "Colonton", "North Garyville", "93354", "casa em condominio", 260069.89, "2021-11-30"),
            imovel_json(3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24")
        ],
        "_links": links_colecao()
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis"
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_listar_imovel_id_ok(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = (
    1,"Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"
    )
    mock_conn.cursor.return_value= mock_cursor
    mock_conectar_banco.return_value = mock_conn

    response =client.get("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == imovel_json(
        1, "Nicole Common", "Travessa", "Lake Danielle", "Judymouth",
        "85184", "casa em condominio", 488423.52, "2017-07-29"
    )

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE id = %s",
        (1,)
    )
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_listar_imoveis_id_erro(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchone.return_value = None
    mock_conn.cursor.return_value= mock_cursor
    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "erro":"Imovel não encontrado",
        "_links": {"imoveis": links_colecao()["self"]}
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE id = %s",
        (999,),
    )
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_adicionar_imovel_ok(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.lastrowid = 10

    mock_conectar_banco.return_value = mock_conn

    imovel = {"logradouro":"Nicole Common","tipo_logradouro":"Travessa","bairro":"Lake Danielle","cidade":"Judymouth","cep":"85184","tipo":"casa em condominio","valor":488423.52,"data_aquisicao":"2017-07-29"}
    response = client.post("/imoveis",json=imovel)

    assert response.status_code == 201
    assert response.get_json() == {
        "id":10,
        "_links": links_imovel(10)
    }

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO imoveis (logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
            ("Nicole Common","Travessa","Lake Danielle","Judymouth","85184","casa em condominio",488423.52,"2017-07-29")
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_adicionar_imovel_erro(mock_conectar_banco,client):
    response = client.post("/imoveis",json={"logradouro":"cachorro"})

    assert response.status_code == 400
    assert response.get_json() == {
        "erro":"Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao",
        "_links": {"criar": links_colecao()["criar"]}
    }

    mock_conectar_banco.assert_not_called()

@patch("main.conectar_banco")
def test_atualizar_imovel_ok(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    imovel = {"logradouro":"Nicole Common","tipo_logradouro":"Travessa","bairro":"Lake Danielle","cidade":"Judymouth","cep":"85184","tipo":"casa em condominio","valor":488423.52,"data_aquisicao":"2017-07-29"}
    response = client.put("/imoveis/1",json=imovel)

    assert response.status_code == 200
    assert response.get_json() == {
        "mensagem":"Imovel atualizado com sucesso",
        "_links": links_imovel(1)
    }

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29", 1)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_atualizar_imovel_erro(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    imovel = {"logradouro":"Nicole Common","tipo_logradouro":"Travessa","bairro":"Lake Danielle","cidade":"Judymouth","cep":"85184","tipo":"casa em condominio","valor":488423.52,"data_aquisicao":"2017-07-29"}
    response = client.put("/imoveis/1",json=imovel)

    assert response.status_code == 404
    assert response.get_json() == {
        "erro":"Imovel não encontrado",
        "_links": {"imoveis": links_colecao()["self"]}
    }

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29", 1)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_remover_imovel_ok(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {
        "mensagem":"Imovel deletado com sucesso",
        "_links": {"imoveis": links_colecao()["self"]}
    }

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = %s",
        (1,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()



@patch("main.conectar_banco")
def test_remover_imovel_erro(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "erro":"Imovel não encontrado",
        "_links": {"imoveis": links_colecao()["self"]}
    }

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = %s",
        (999,)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

        
@patch("main.conectar_banco")
def test_listar_imovel_tipo_ok(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        (3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24")
    ]

    response = client.get("/imoveis?tipo=apartamento")

    assert response.status_code == 200
    assert response.get_json() == {
        "imoveis": [
            imovel_json(3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24")
        ],
        "_links": links_colecao()
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE tipo = %s",
        ("apartamento",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("main.conectar_banco")
def test_listar_imovel_tipo_erro(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/imoveis?tipo=apartamento")

    assert response.status_code == 404
    assert response.get_json() == {
        "erro":"Não foi encontrado este tipo de imovel.",
        "_links": {"imoveis": links_colecao()["self"]}
    }
    

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE tipo = %s",
        ("apartamento",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()



@patch("main.conectar_banco")
def test_listar_imovel_cidade_ok(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        (3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24")
    ]

    response = client.get("/imoveis?cidade=Katherinefurt")

    assert response.status_code == 200
    assert response.get_json() == {
        "imoveis": [
            imovel_json(3, "Taylor Ranch", "Avenida", "West Jennashire", "Katherinefurt", "51116", "apartamento", 815969.92, "2020-04-24")
        ],
        "_links": links_colecao()
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE cidade = %s",
        ("Katherinefurt",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("main.conectar_banco")
def test_listar_imovel_cidade_erro(mock_conectar_banco,client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conectar_banco.return_value = mock_conn

    mock_cursor.fetchall.return_value = []

    response = client.get("/imoveis?cidade=Katherinefurt")

    assert response.status_code == 404
    assert response.get_json() == {
        "erro":"A cidade não foi encontrada na lista de imóveis.",
        "_links": {"imoveis": links_colecao()["self"]}
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE cidade = %s",
        ("Katherinefurt",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("main.conectar_banco")
def test_atualizar_imovel_dados_incompletos(mock_conectar_banco,client):
    imovel_incompleto = {"logradouro":"Nicole Common"}

    response = client.put("/imoveis/1",json=imovel_incompleto)

    assert response.status_code == 400
    assert response.get_json() == {
        "erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao",
        "_links": {
            "corrigir": {"href": "/imoveis/1", "method": "PUT"},
            "imoveis": links_colecao()["self"]
        }
    }

    mock_conectar_banco.assert_not_called()
