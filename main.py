import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask,jsonify,request

load_dotenv()

app = Flask(__name__)

def conectar_banco():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database =os.getenv("DB_NAME"),
        ssl_ca=os.getenv("DB_SSL_CA"),
        port=int(os.getenv("DB_PORT"))
    )
    return conn

def buscar_todos(cursor):
    cursor.execute( 
    "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis"
    )
    return cursor.fetchall()

def buscar_por_tipo(cursor, tipo):
    cursor.execute(
    "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE tipo = %s",
    (tipo,)
    )
    return cursor.fetchall()

def buscar_por_cidade(cursor, cidade):
    cursor.execute(
    "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE cidade = %s",
    (cidade,)
    )
    return cursor.fetchall()

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

def formatar_imovel(imovel):
    return {
        "id": imovel[0],
        "logradouro": imovel[1],
        "tipo_logradouro": imovel[2],
        "bairro": imovel[3],
        "cidade": imovel[4],
        "cep": imovel[5],
        "tipo": imovel[6],
        "valor": imovel[7],
        "data_aquisicao": imovel[8],
        "_links": links_imovel(imovel[0])
    }

@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    tipo = request.args.get("tipo")
    cidade = request.args.get("cidade")

    conn = conectar_banco()
    cursor = conn.cursor()

    if tipo:
        imoveis = buscar_por_tipo(cursor, tipo)
    elif cidade:
        imoveis = buscar_por_cidade(cursor, cidade)
    else:
        imoveis = buscar_todos(cursor)

    cursor.close()
    conn.close()

    if tipo and len(imoveis) == 0:
        return jsonify({
            "erro": "Não foi encontrado este tipo de imovel.",
            "_links": {"imoveis": links_colecao()["self"]}
        }), 404

    if cidade and len(imoveis) == 0:
        return jsonify({
            "erro": "A cidade não foi encontrada na lista de imóveis.",
            "_links": {"imoveis": links_colecao()["self"]}
        }), 404

    imoveis_formatados = [formatar_imovel(imovel) for imovel in imoveis]

    return jsonify({
        "imoveis": imoveis_formatados,
        "_links": links_colecao()
    }), 200

@app.route("/imoveis/<int:id>", methods=["GET"])
def listar_imoveis_id(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute( 
    "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE id = %s",
    (id,)
    )

    imovel = cursor.fetchone()

    cursor.close()
    conn.close()

    if imovel is None:
        return jsonify({
            "erro":"Imovel não encontrado",
            "_links": {"imoveis": links_colecao()["self"]}
        }), 404

    imovel_formatado = formatar_imovel(imovel)

    return jsonify(imovel_formatado),200


@app.route("/imoveis", methods=["POST"])
def adicionar_imovel():
    novo = request.json or {}

    if "logradouro" not in novo or "tipo_logradouro" not in novo or "bairro" not in novo or "cidade" not in novo or "cep" not in novo or "tipo" not in novo or "valor" not in novo or "data_aquisicao" not in novo:
        return jsonify({
            "erro":"Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao",
            "_links": {"criar": links_colecao()["criar"]}
        }),400

    conn = conectar_banco()
    cursor= conn.cursor()

    cursor.execute(
        "INSERT INTO imoveis (logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
        (novo["logradouro"],novo["tipo_logradouro"],novo["bairro"],novo["cidade"],novo["cep"],novo["tipo"],novo["valor"],novo["data_aquisicao"])
    )

    conn.commit()
    novo_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "id":novo_id,
        "_links": links_imovel(novo_id)
    }),201


@app.route("/imoveis/<int:id>", methods=["PUT"])
def atualizar_imovel(id):
    novo = request.json or {}

    if (
        "logradouro" not in novo
        or "tipo_logradouro" not in novo
        or "bairro" not in novo
        or "cidade" not in novo
        or "cep" not in novo
        or "tipo" not in novo
        or "valor" not in novo
        or "data_aquisicao" not in novo
    ):
        return jsonify({
            "erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao",
            "_links": {
                "corrigir": {"href": f"/imoveis/{id}", "method": "PUT"},
                "imoveis": links_colecao()["self"]
            }
        }), 400

    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        (
            novo["logradouro"],
            novo["tipo_logradouro"],
            novo["bairro"],
            novo["cidade"],
            novo["cep"],
            novo["tipo"],
            novo["valor"],
            novo["data_aquisicao"],
            id
        )
    )

    conn.commit()
    linha = cursor.rowcount

    cursor.close()
    conn.close()

    if linha == 0:
        return jsonify({
            "erro": "Imovel não encontrado",
            "_links": {"imoveis": links_colecao()["self"]}
        }), 404

    return jsonify({
        "mensagem": "Imovel atualizado com sucesso",
        "_links": links_imovel(id)
    }), 200

@app.route("/imoveis/<int:id>", methods=["DELETE"])
def remover_imovel(id):
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM imoveis WHERE id = %s",
        (id,)
    )

    conn.commit()
    linhas = cursor.rowcount

    cursor.close()
    conn.close()

    if linhas == 0:
        return jsonify({
            "erro":"Imovel não encontrado",
            "_links": {"imoveis": links_colecao()["self"]}
        }), 404

    return jsonify({
        "mensagem": "Imovel deletado com sucesso",
        "_links": {"imoveis": links_colecao()["self"]}
    }),200

if __name__ == "__main__":
    app.run(debug=True)