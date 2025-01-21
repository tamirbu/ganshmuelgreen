from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import os, uuid
import json
import csv
from pathlib import Path
from typing import Union, List, Tuple, Dict
from datetime import datetime

app = Flask(__name__)

# MySQL configurations from environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DATABASE')

# Initialize MySQL
mysql = MySQL(app)

def convert_to_kg(weight: Union[int, float, str], unit: str = 'kg') -> int:
    """
    Convert weight to kilograms
    Args:
        weight: The weight value to convert
        unit: The unit of the weight (kg/lbs), defaults to 'kg'
    Returns:
        Weight in kilograms as integer
    """
    weight = float(weight)
    if unit.lower() == 'lbs':
        return int(weight * 0.453592)
    return int(weight)

@app.route('/health', methods=['GET'])
def health():
    return "OK", 200
        

@app.route('/weight', methods=['GET'])
def get_weights():
    try:
        t1 = request.args.get('from', datetime.now().strftime('%Y%m%d') + "000000")
        t2 = request.args.get('to', datetime.now().strftime('%Y%m%d%H%M%S'))
        f = request.args.get('filter', 'in,out,none').split(',')

        try:
            t1_formatted = datetime.strptime(t1, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
            t2_formatted = datetime.strptime(t2, '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as ve:
            return jsonify({"error": "Invalid date format. Expected format: YYYYMMDDHHMMSS"}), 400

        if not f or all(not direction for direction in f):
            return jsonify({"error": "Filter parameter cannot be empty"}), 400

        cursor = mysql.connection.cursor()
        query = f"""
            SELECT id, direction, bruto, neto, produce, containers
            FROM transactions
            WHERE datetime BETWEEN %s AND %s
              AND direction IN ({','.join(['%s'] * len(f))})
        """
        cursor.execute(query, [t1_formatted, t2_formatted, *f])
        results = cursor.fetchall()
        cursor.close()

        output = []
        for row in results:
            containers = row[5].split(',') if row[5] else [] 
            neto = row[3] if row[3] is not None else "na"
            output.append({
                "id": row[0],
                "direction": row[1],
                "bruto": row[2],
                "neto": neto,
                "produce": row[4],
                "containers": containers
            })

        return jsonify(output), 200

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/unknown', methods=['GET'])
def get_unknown_containers():
        cursor = mysql.connection.cursor()
        cursor.execute("""
        SELECT container_id
        FROM containers_registered
        WHERE weight IS NULL OR weight = 0
        """
        )
        result = cursor.fetchall()    
        cursor.close()
        container_ids = [row[0] for row in result]
        return jsonify(container_ids), 200

@app.route('/item/<id>', methods=['GET'])
def get_item(id):
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    tz = pytz.timezone('Israel')
    now = datetime.now(tz)

    def parse_date_with_time(date_str):
        if date_str:
            if len(date_str) != 14:  # yyyymmddhhmmss should be 14 characters
                raise ValueError("Invalid date format. Use yyyymmddhhmmss.")
            try:
                return tz.localize(datetime.strptime(date_str, '%Y%m%d%H%M%S'))
            except ValueError:
                raise ValueError("Invalid date format. Use yyyymmddhhmmss.")
        return None

    # Parse from_date
    if from_date:
        from_date = parse_date_with_time(from_date)
        if from_date is None:
            return jsonify({"error": "from_date must include time when provided."}), 400
    else:
        from_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Parse to_date
    if to_date:
        to_date = parse_date_with_time(to_date)
        if to_date is None:
            return jsonify({"error": "to_date must include time when provided."}), 400
    else:
        to_date = now

    # Check if to_date is earlier than from_date
    if to_date < from_date:
        return jsonify({"error": "to_date cannot be earlier than from_date."}), 400

    try:
        # Check if the item is a truck or a container
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT id FROM Trucks WHERE id = %s", (id,))
        is_truck = cur.fetchone() is not None
        cur.close()

        if is_truck:
            # Get the last known tara for truck
            cur = mysql.connection.cursor(dictionary=True)
            cur.execute("""
                SELECT truckTara as tara
                FROM Transactions
                WHERE truck = %s AND truckTara IS NOT NULL
                ORDER BY datetime DESC
                LIMIT 1
            """, (id,))
            tara_result = cur.fetchone()
            cur.close()
            tara = tara_result['tara'] if tara_result else "na"

            # Get sessions for truck
            cur = mysql.connection.cursor(dictionary=True)
            cur.execute("""
                SELECT id
                FROM Transactions
                WHERE truck = %s AND datetime BETWEEN %s AND %s
                ORDER BY datetime
            """, (id, from_date, to_date))
            sessions = [row['id'] for row in cur.fetchall()]
            cur.close()
        else:
            # Check if it's a container
            cur = mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT weight as tara FROM Containers WHERE container_id = %s", (id,))
            tara_result = cur.fetchone()
            cur.close()
            
            if tara_result is None:
                return jsonify({"error": "Item not found"}), 404
            
            tara = tara_result['tara']

            # Get sessions for container
            cur = mysql.connection.cursor(dictionary=True)
            cur.execute("""
                SELECT id
                FROM Transactions
                WHERE containers LIKE %s AND datetime BETWEEN %s AND %s
                ORDER BY datetime
            """, (f'%{id}%', from_date, to_date))
            sessions = [row['id'] for row in cur.fetchall()]
            cur.close()

        return jsonify({
            "id": id,
            "tara": tara,
            "sessions": sessions
        })

    except Exception as e:
        print(f"Database error: {e}")

@app.route('/session/<id>', methods=['GET'])
def get_session(id):
    try:
        cursor= mysql.connection.cursor()
        cursor.execute("SELECT * FROM transactions WHERE id = %s", (id,))
        session = cursor.fetchone()
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        column_names = [desc[0] for desc in cursor.description]
        session_dict = dict(zip(column_names, session))

        response = {
            "id": session_dict["id"],
            "truck": session_dict["truck"] if session_dict["truck"] else "na",
            "bruto": session_dict["bruto"],
        }

        if session_dict["direction"] == "out":
            response["truckTara"] = session_dict["truckTara"]
            if session_dict["neto"] =="None":
               response["neto"] = "na"
            else:   
               response["neto"] = session_dict["neto"]

        return jsonify(response),200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

def process_csv_file(file_path: Path) -> List[Tuple[str, int]]:
    """
    Process CSV file and return list of (container_id, weight_kg) tuples
    Supports both formats:
    - id,weight
    - id,weight,unit
    """
    records = []
    try:
        with open(file_path, 'r') as f:
            csv_reader = csv.reader(f)
            header = next(csv_reader, None)  # Skip header if exists
            
            # Check if header exists and skip if it does
            if header and header[0].lower() == 'id':
                pass
            else:
                # If no header, process the first row as data
                process_row(header, records)  # Process the header row as data
            
            # Process remaining rows
            for row in csv_reader:
                process_row(row, records)
                
    except Exception as e:
        raise ValueError(f"Error processing CSV file: {str(e)}")
        
    return records

def process_row(row: List[str], records: List[Tuple[str, int]]) -> None:
    """Helper function to process a single CSV row"""
    if not row:
        return
        
    if len(row) >= 3:  # Format: id,weight,unit
        container_id, weight, unit = row[0], row[1], row[2]
        weight_kg = convert_to_kg(weight, unit)
    else:  # Format: id,weight (assuming kg)
        container_id, weight = row[0], row[1]
        weight_kg = convert_to_kg(weight)
        
    records.append((container_id, weight_kg))

def process_json_file(file_path: Path) -> List[Tuple[str, int]]:
    """
    Process JSON file and return list of (container_id, weight_kg) tuples
    Expected format: [{"id": "...", "weight": ..., "unit": "..."}]
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON file must contain an array of objects")
                
            records = []
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("Each item in JSON must be an object")
                if 'id' not in item or 'weight' not in item:
                    raise ValueError("Each item must have 'id' and 'weight' fields")
                    
                weight_kg = convert_to_kg(item['weight'], item.get('unit', 'kg'))
                records.append((item['id'], weight_kg))
            return records
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing JSON file: {str(e)}")

# Helper function to calculate Neto
def calculate_neto(bruto, truck_tara, container_taras):
    if any(tara is None for tara in container_taras):
        return None  # If any container's tara is unknown
    print (bruto, truck_tara, container_taras)
    return bruto - truck_tara - sum(container_taras)

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
        containers= [cw[0] for cw in container_weights]
        neto = calculate_neto(bruto, weight,containers)

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

@app.route('/batch-weight', methods=['POST'])
def batch_weight() -> tuple:
    """
    Process a batch file containing container tara weights
    Accepts CSV files (id,kg/id,weight,unit) and JSON files
    """
    try:
        # Validate request
        if 'file' not in request.form:
            return jsonify({"error": "No file specified"}), 400
            
        filename = request.form['file']
        file_path = Path('/app/in') / filename
        
        # Validate file exists
        if not file_path.exists():
            return jsonify({"error": f"File {filename} not found in /in folder"}), 404

        # Process file based on extension
        ext = file_path.suffix.lower()
        if ext == '.json':
            records = process_json_file(file_path)
        elif ext == '.csv':
            records = process_csv_file(file_path)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Update database
        cursor = mysql.connection.cursor()
        try:
            for container_id, weight in records:
                cursor.execute(
                    """INSERT INTO containers_registered 
                       (container_id, weight, unit) 
                       VALUES (%s, %s, 'kg')
                       ON DUPLICATE KEY UPDATE weight=%s, unit='kg'""",
                    (container_id, weight, weight)
                )
            
            mysql.connection.commit()
            return jsonify({"message": f"Successfully processed {len(records)} records"}), 200
            
        except Exception as db_error:
            mysql.connection.rollback()
            raise db_error
        finally:
            cursor.close()

    except Exception as e:
        print(f"Error in batch-weight: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Verify database connection on startup
    try:
        with app.app_context():  # This ensures you are inside the app context
            cursor = mysql.connection.cursor()
            print("Successfully connected to MySQL database!")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)
