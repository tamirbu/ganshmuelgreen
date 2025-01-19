from flask import Flask, request, jsonify
import mysql.connector
import os
import pandas as pd


app = Flask(__name__)

#db connaction-------------------------------------------------------------------------------------
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

# add provider to tabel - post------------------------------------------------------------------------
@app.route("/provider", methods=["POST"])
def add_provider():
    # get the name 
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({f"error": "Missing provider name"}), 400

    provider_name = data["name"]

    try:
        # open the connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # add provider to table
        query = "INSERT INTO Provider (name) VALUES (%s)"
        cursor.execute(query, (provider_name,))
        conn.commit()

        # get the id random
        provider_id = cursor.lastrowid

        # close connaction
        cursor.close()
        conn.close()

        # return json new provider
        return jsonify({"id": provider_id, "name": provider_name}), 201

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


    print("Received request to upload rates...")  # debug message
    file_path = "/app/in/rates.xlsx"
    
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File {file_path} not found")  # debug message
        return jsonify({"error": f"File {file_path} not found"}), 404

    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        print(f"File read successfully, data: {df.head()}")  # debug message
        
        for index, row in df.iterrows():
            product = row["Product"]
            rate = row["Rate"]
            scope = row["Scope"]

            # Determine the scope (ALL or provider-specific)
            if scope == "ALL":
                cursor.execute("DELETE FROM Rates WHERE product_id = %s AND (scope IS NULL OR scope = 'ALL')", (product,))
                cursor.execute("INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, 'ALL')", (product, rate))
            else:
                cursor.execute("DELETE FROM Rates WHERE product_id = %s AND scope = %s", (product, scope))
                cursor.execute("INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, %s)", (product, rate, scope))

        conn.commit()

        return jsonify({"message": "Rates updated successfully!"}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # debug message
        return jsonify({"error": str(e)}), 500



    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # קריאת הקובץ ישירות מה-request
        df = pd.read_excel(file)
        print(f"File read successfully, data: {df.head()}")
        
        # יצירת חיבור למסד הנתונים
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for index, row in df.iterrows():
            product = row["Product"]
            rate = row["Rate"]
            scope = row["Scope"]
            
            if scope == "ALL":
                cursor.execute("DELETE FROM Rates WHERE product_id = %s AND (scope IS NULL OR scope = 'ALL')", (product,))
                cursor.execute("INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, 'ALL')", (product, rate))
            else:
                cursor.execute("DELETE FROM Rates WHERE product_id = %s AND scope = %s", (product, scope))
                cursor.execute("INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, %s)", (product, rate, scope))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Rates updated successfully!"}), 200

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


    # print("Received POST request at /rates")  # הודעת דיבוג
    file_path = "./in/rates.xlsx"
    return "Welcome rates!"
    
    # # Check if the file exists
    # if not os.path.exists(file_path):
    #     return jsonify({"error": f"File {file_path} not found"}), 404
    
    # try:
    #     # Read the Excel file
    #     df = pd.read_excel(file_path)
    #     print("Excel file read successfully")  # הודעת דיבוג

    #     for index, row in df.iterrows():
    #         product = row["Product"]
    #         rate = row["Rate"]
    #         scope = row["Scope"]

    #         # Determine the scope (ALL or provider-specific)
    #         if scope == "ALL":
    #             # Update ALL rate (lower precedence)
    #             cursor.execute("DELETE FROM Rates WHERE product_id = %s AND (scope IS NULL OR scope = 'ALL')", (product,))
    #             cursor.execute("INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, 'ALL')", (product, rate))
    #         else:
    #             # Update provider-specific rate (higher precedence)
    #             cursor.execute("DELETE FROM Rates WHERE product_id = %s AND scope = %s", (product, scope))
    #             cursor.execute("INSERT INTO Rates (product_id, rate, scope) VALUES (%s, %s, %s)", (product, rate, scope))

    #     # Commit the changes
    #     conn.commit()
    #     print("Rates updated successfully!")  # הודעת דיבוג

    #     return jsonify({"message": "Rates updated successfully!"}), 200

    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500

# home page--------------------------------------------------------------------------------------
@app.route("/")
def index():
    return "Welcome to the Flask App!"

# chack health------------------------------------------------------------------------------------
@app.route("/health")
def health_check():
    return jsonify({"status": "OK"}), 200

# main--------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
