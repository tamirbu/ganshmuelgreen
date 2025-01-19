from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import os, uuid, csv

csv_file_path = "./sample_files/sample_uploads/containers1.csv"

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DATABASE')

# Initialize MySQL
mysql = MySQL(app)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns "OK" if the database is accessible, otherwise "Failure".
    """
    try:
        with app.app_context():
            # Check database connection
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
        return jsonify(status="OK"), 200
    except Exception as e:
        return jsonify(status="Failure", error=str(e)), 500


# Helper function to calculate Neto
def calculate_neto(bruto, truck_tara, container_taras):
    #if any(tara is None for tara in container_taras):
        #return None  # If any container's tara is unknown
    print (bruto, truck_tara, container_taras)
    return bruto - truck_tara - sum(container_taras)


# Function to load containers from a CSV file
def load_containers_from_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                container_id = row["id"]
                if "kg" in row:
                    weight_kg = float(row["kg"])
                elif "lbs" in row:
                    weight_kg = float(row["lbs"]) * 0.453592
                else:
                    continue
                # Insert into database directly
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO containers_registered (container_id, weight) VALUES (%s, %s)", (container_id, weight_kg))
                mysql.connection.commit()
                cursor.close()
        print(f"Loaded containers from {file_path}")
    except Exception as e:
        print(f"Error loading containers: {e}")


# API routes
@app.route('/weight', methods=['POST'])
def post_weight():
    data = request.get_json()
    direction = data.get("direction")
    truck = data.get("truck", "na")
    containers_list = data.get("containers", "").split(",") if "containers" in data else []
    weight = data.get("weight")
    unit = data.get("unit", "kg")
    force = data.get("force", False)
    produce = data.get("produce", "na")

    # Validate input
    if direction not in {"in", "out", "none"}:
        return jsonify({"error": "Invalid direction"}), 400
    if not isinstance(weight, int):
        return jsonify({"error": "Invalid weight"}), 400
    if unit not in {"kg", "lbs"}:
        return jsonify({"error": "Invalid unit"}), 400

    # Convert to kg if needed
    if unit == "lbs":
        weight = float(weight * 0.453592)

    session_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    # Handle "none"
    if direction == "none":
        query = """
                INSERT INTO transactions (datetime, direction, bruto)
                VALUES (%s, %s, %s)
                """
        cursor = mysql.connection.cursor()
        cursor.execute(query, (timestamp, direction, weight))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"session_id": session_id}), 200

    # Handle "in"
    if direction == "in":
        query = """
                INSERT INTO transactions (datetime, direction, truck, containers, bruto, produce)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
        containers_str = ",".join(containers_list)
        cursor = mysql.connection.cursor()
        cursor.execute(query, (timestamp, direction, truck, containers_str, weight, produce))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"session_id": session_id}), 200

    # Handle "out"
    if direction == "out":
        cursor = mysql.connection.cursor()
        cursor.execute("""
                SELECT id, bruto FROM transactions WHERE truck = %s AND direction = 'in' ORDER BY datetime DESC LIMIT 1
                """, (truck,))
        previous_session = cursor.fetchone()
        if not previous_session:
            return jsonify({"error": "'out' without 'in' is not allowed"}), 400
        previous_id, bruto = previous_session
        cursor.execute("""
                SELECT weight FROM containers_registered WHERE container_id IN (%s)
                """, (",".join(containers_list),))
        container_weights = cursor.fetchall()
        print(f'container list{container_weights}')
        neto = calculate_neto(bruto, weight, [cw[0] for cw in container_weights])

        query = """
                INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
        containers_str = ",".join(containers_list)
        cursor.execute(query, (timestamp, direction, truck, containers_str, bruto, weight, neto, produce))
        mysql.connection.commit()
        cursor.close()

        # Fetching the data for the session
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT * FROM transactions WHERE truck = %s ORDER BY datetime DESC LIMIT 1
        """, (truck,))
        transaction = cursor.fetchone()
        cursor.close()
        
        # Return transaction details
        if transaction:
            return jsonify({
                "session_id": session_id,
                "truck": transaction[2],  # truck
                "direction": transaction[1],  # direction
                "bruto": transaction[4],  # bruto
                "neto": transaction[7],  # neto
                "produce": transaction[8]  # produce
            }), 200

    return jsonify({"error": "Invalid request"}), 400


if __name__ == '__main__':
    # Verify database connection
    try:
        with app.app_context():  # This ensures you are inside the app context
            cursor = mysql.connection.cursor()
            print("Successfully connected to MySQL database!")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")

# Load containers from CSV with app context
    #try:
        #with app.app_context():  # Ensure we are in the correct context when loading containers
            #load_containers_from_csv(csv_file_path)
    #except Exception as e:
        #print(f"Error loading containers: {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)
