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

@app.route("/imoveis/<int:id>", methods=["GET", "PUT", "DELETE"])
def listar_por_id(id):
    if request.method == "GET":
        conn   = conectar_banco()
        cursor = conn.cursor(dictionary=True)  
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
    
    if request.method == "PUT":
        data = request.get_json()
        conn   = conectar_banco()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "UPDATE imoveis SET logradouro = ?, tipo_logradouro = ?, "
            "bairro = ?, cidade = ?, cep = ?, tipo = ?, valor = ?, "
            "data_aquisicao = ? WHERE id = ?",
            (
                data["logradouro"], data["tipo_logradouro"], data["bairro"],
                data["cidade"], data["cep"], data["tipo"],
                data["valor"], data["data_aquisicao"], id
            )
        )
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()

        if rows_affected == 0:
            return jsonify({"error": "Imóvel não encontrado"}), 404

        return jsonify({"mensagem": "Imóvel atualizado com sucesso!"}), 200

    if request.method == "DELETE":
        conn   = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM imoveis WHERE id = ?", (id,))
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()

        if rows_affected == 0:
            return jsonify({"error": "Imóvel não encontrado"}), 404

        return jsonify({"mensagem": "Imóvel deletado com sucesso!"}), 200

@app.route("/imoveis/add", methods=["POST"])
def adicionar_imovel():
    data = request.get_json()

    if not all(key in data for key in ["logradouro", "tipo_logradouro", "bairro", "cidade", "cep", "tipo", "valor", "data_aquisicao"]):
        return jsonify({"error": "Dados incompletos"}), 400

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