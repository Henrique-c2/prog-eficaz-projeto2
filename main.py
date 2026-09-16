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