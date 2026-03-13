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

@app.route("/imoveis/<int:id>", methods=["GET"])
def listar_por_id(id):
    conn   = conectar_banco()
    cursor = conn.cursor()  
    cursor.execute(
        "SELECT id, logradouro, tipo_logradouro, bairro, cidade, "
        "cep, tipo, valor, data_aquisicao FROM imoveis WHERE id = %s",
        (id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return jsonify(row)
    else:
        return jsonify({"error": "Imóvel não encontrado"}), 404
    
@app.route("/imoveis/add", methods=["POST"])
def adicionar_imovel():
    data = request.get_json()
    conn   = conectar_banco()
    cursor = conn.cursor()  
    cursor.execute(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, "
        "cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            data["logradouro"], data["tipo_logradouro"], data["bairro"],
            data["cidade"], data["cep"], data["tipo"],
            data["valor"], data["data_aquisicao"]
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Imóvel adicionado com sucesso!"}), 201
    
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/imoveis/update/<int:id>", methods=["PUT"])
def atualizar_imovel(idl):
    data = request.get_json()
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, "
        "cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s "
        "WHERE id = %s",
        (
            data["logradouro"], data["tipo_logradouro"], data["bairro"],
            data["cidade"], data["cep"], data["tipo"],
            data["valor"], data["data_aquisicao"], id
        )
    )
    conn.commit()
    cursor.close()  
    conn.close()
    return jsonify({"message": "Imóvel atualizado com sucesso!"})

    
    