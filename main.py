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

@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conn = conectar_banco()
    cursor = conn.cursor()

    cursor.execute( 
    "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis"
    )
    imoveis = cursor.fetchall()

    cursor.close()
    conn.close()

    imoveis_formatados = [
    {
        "id": imoveis[0],
        "logradouro": imoveis[1],
        "tipo_logradouro": imoveis[2],
        "bairro": imoveis[3],
        "cidade": imoveis[4],
        "cep": imoveis[5],
        "tipo": imoveis[6],
        "valor": imoveis[7],
        "data_aquisicao": imoveis[8]
    }
    for imovel in imoveis
    ]

    return jsonify(imoveis_formatados), 200

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
            "erro":"Imovel não encontrado"
        }), 404

    imovel_formatado = {
        "id": imovel[0],
        "logradouro": imovel[1],
        "tipo_logradouro": imovel[2],
        "bairro": imovel[3],
        "cidade": imovel[4],
        "cep": imovel[5],
        "tipo": imovel[6],
        "valor": imovel[7],
        "data_aquisicao": imovel[8]
    }

    return jsonify(imovel_formatado),200


@app.route("/imoveis", methods=["POST"])
def adicionar_imovel():
    novo = request.json or {}

    if "logradouro" not in novo or "tipo_logradouro" not in novo or "bairro" not in novo or "cidade" not in novo or "cep" not in novo or "tipo" not in novo or "valor" not in novo or "data_aquisicao" not in novo:
        return jsonify({"erro":"Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}),400

    conn = conectar_banco()
    cursor= conn.cursor()

    cursor.execute(
        "INSERT INTO imoveis (logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
        (novo["logradouro"],novo["tipo_logradouro"],novo["bairro"],novo["cidade"],novo["cep"],novo["tipo"],novo["valor"],novo["data_aquisicao"])
    )

    conn.commit
    novo_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({"id":novo_id}),200


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
            "erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"
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
            "erro": "Imovel não encontrado"
        }), 404

    return jsonify({
        "mensagem": "Imovel atualizado com sucesso"
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
            "erro":"Imovel não encontrado."
        })

    return jsonify({
        "mensagem": "Imovel deletado com sucesso"
    }),200

@app.route("/imoveis", methods=["GET"])
def listar_imovel_tipo():
    tipo = request.args.get("tipo")

    conn = conectar_banco()
    cursor = conn.cursor()

    if tipo:
        cursor.execute(
            "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE tipo = %s",
            (tipo,)
        )
    else:
        cursor.execute(
            "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis"
        )

    imoveis = cursor.fetchall()

    cursor.close()
    conn.close()

    if tipo and len(imoveis) == 0:
        return jsonify({
            "erro": "Não foi encontrado este tipo de imovel."
        }), 404

    imoveis_formatados = [
        {
            "id": imovel[0],
            "logradouro": imovel[1],
            "tipo_logradouro": imovel[2],
            "bairro": imovel[3],
            "cidade": imovel[4],
            "cep": imovel[5],
            "tipo": imovel[6],
            "valor": imovel[7],
            "data_aquisicao": imovel[8]
        }
        for imovel in imoveis
    ]

    return jsonify(imoveis_formatados), 200

@app.route("/imoveis",methods = ["GET"])
def listar_imovel_cidade():
    cidade = request.args.get("cidade")

    conn = conectar_banco()
    cursor = conn.cursor()

    if cidade:
        cursor.execute(
            "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis WHERE cidade = %s",
            (cidade,)
        )
    else:
        cursor.execute(
            "SELECT id,logradouro,tipo_logradouro,bairro,cidade,cep,tipo,valor,data_aquisicao FROM imoveis"
        )

    imoveis = cursor.fetchall()

    cursor.close()
    conn.close()

    if cidade and len(imoveis) == 0:
        return jsonify({
            "erro": "Não foi encontrado este cidade de imovel."
        }), 404

    imoveis_formatados = [
        {
            "id": imovel[0],
            "logradouro": imovel[1],
            "tipo_logradouro": imovel[2],
            "bairro": imovel[3],
            "cidade": imovel[4],
            "cep": imovel[5],
            "tipo": imovel[6],
            "valor": imovel[7],
            "data_aquisicao": imovel[8]
        }
        for imovel in imoveis
    ]

    return jsonify(imoveis_formatados), 200