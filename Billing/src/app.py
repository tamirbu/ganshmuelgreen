from flask import Flask, request, jsonify
import mysql.connector
import os

app = Flask(__name__)

db_host = os.getenv("DATABASE_HOST", "localhost")
db_port = os.getenv("DATABASE_PORT", "3306")
db_name = os.getenv("DATABASE_NAME", "mydatabase")
db_user = os.getenv("DATABASE_USER", "myuser")
db_password = os.getenv("DATABASE_PASSWORD", "mypassword")

def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )

@app.route("/provider", methods=["POST"])
def add_provider():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({f"error": "Missing provider name"}), 400

    provider_name = data["name"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO Provider (name) VALUES (%s)"
        cursor.execute(query, (provider_name,))
        conn.commit()

        provider_id = cursor.lastrowid  # קבלת ה-ID החדש

        cursor.close()
        conn.close()

        return jsonify({"id": provider_id, "name": provider_name}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    
@app.route("/")
def index():
    return "Welcome to the Flask App!"


@app.route("/health")
def health_check():
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
