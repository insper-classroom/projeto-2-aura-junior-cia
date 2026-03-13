from flask import Flask, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "port":     int(os.getenv("DB_PORT")),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "ssl_ca":   os.getenv("DB_SSL_CA"),
}


def conectar_banco():
    """Retorna uma conexão com o MySQL do Aiven."""
    return mysql.connector.connect(**DB_CONFIG)


# ── GET /imoveis ──────────────────────────────────────────────────────────────
@app.route("/imoveis", methods=["GET"])
def listar_imoveis():
    conn   = conectar_banco()
    cursor = conn.cursor(dictionary=True)  
    cursor.execute(
        "SELECT id, logradouro, tipo_logradouro, bairro, cidade, "
        "cep, tipo, valor, data_aquisicao FROM imoveis"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)