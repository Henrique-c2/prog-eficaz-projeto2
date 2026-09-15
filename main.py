import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask

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