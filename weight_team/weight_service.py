from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import os
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
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return "OK", 200
    except Exception as e:
        return "Failure", 500
        

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
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
        SELECT container_id
        FROM containers_registered
        WHERE weight IS NULL OR weight = 0
        """)
        result = cursor.fetchall()
        container_ids = [row[0] for row in result]
        return jsonify(container_ids), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        cursor.close()

@app.route('/item/<id>', methods=['GET'])
def get_item(id):
    """Get information about a specific truck or container"""
    cursor = None
    try:
        # Get date range parameters with defaults
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        
        if not from_date:  
            from_date = datetime.now().replace(day=1, hour=0, minute=0, second=0).strftime('%Y%m%d%H%M%S')
        if not to_date:
            to_date = datetime.now().strftime('%Y%m%d%H%M%S')
        
        try:
            # Validate and convert dates  
            from_datetime = datetime.strptime(from_date, '%Y%m%d%H%M%S') 
            to_datetime = datetime.strptime(to_date, '%Y%m%d%H%M%S')
            
            if to_datetime < from_datetime:
                return jsonify({"error": "to_date cannot be earlier than from_date"}), 400
                
            from_date = from_datetime.strftime('%Y-%m-%d %H:%M:%S')
            to_date = to_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
        except ValueError as e:
            return jsonify({"error": "Invalid date format. Use YYYYMMDDhhmmss"}), 400

        # Create cursor after date validation
        cursor = mysql.connection.cursor()
        
        # First check if id exists as a container
        cursor.execute("""
            SELECT weight as tara 
            FROM containers_registered 
            WHERE container_id = %s
        """, (id,))
        container_result = cursor.fetchone()
        
        if container_result:
            # Handle container case
            tara = container_result[0] if container_result[0] is not None else "na" 
            
            # Get container's sessions using FIND_IN_SET or LIKE
            cursor.execute("""
                SELECT id 
                FROM transactions 
                WHERE (FIND_IN_SET(%s, containers) > 0
                    OR containers = %s
                    OR containers LIKE %s
                    OR containers LIKE %s  
                    OR containers LIKE %s)
                AND datetime BETWEEN %s AND %s
                ORDER BY datetime  
            """, (id, id, f"{id},%", f"%,{id},%", f"%,{id}", from_date, to_date))
                
        else:
            # Check if exists as a truck
            cursor.execute("""
                SELECT DISTINCT truck 
                FROM transactions 
                WHERE truck = %s
                LIMIT 1
            """, (id,))  
            truck_exists = cursor.fetchone()
            
            if not truck_exists:
                return jsonify({"error": "Item not found"}), 404
            
            # Get truck's last known tara  
            cursor.execute("""
                SELECT truckTara as tara 
                FROM transactions 
                WHERE truck = %s 
                AND truckTara IS NOT NULL 
                ORDER BY datetime DESC 
                LIMIT 1
            """, (id,))
            tara_result = cursor.fetchone()
            tara = tara_result[0] if tara_result and tara_result[0] is not None else "na"
            
            # Get truck's sessions
            cursor.execute("""
                SELECT id 
                FROM transactions 
                WHERE truck = %s 
                AND datetime BETWEEN %s AND %s 
                ORDER BY datetime
            """, (id, from_date, to_date))
        
        sessions = [str(row[0]) for row in cursor.fetchall()]
        
        response = {
            "id": id,
            "tara": tara,
            "sessions": sessions
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Detailed error in get_item: {str(e)}")  # More detailed error logging
        return jsonify({"error": "An error occurred while processing the request"}), 500
    finally:
        if cursor:
            cursor.close()


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
            if session_dict["neto"] is None:
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
        weight = int(weight * 0.453592)

    timestamp = datetime.now().isoformat()

    cursor = mysql.connection.cursor()

    # Handle "none"
    if direction == "none":
        cursor.execute("""
            SELECT id FROM transactions WHERE truck = %s AND direction = 'in' ORDER BY datetime DESC LIMIT 1
        """, (truck,))
        last_in_session = cursor.fetchone()

        if last_in_session:
            return jsonify({"error": "'none' after 'in' is not allowed"}), 400

        query = """
            INSERT INTO transactions (datetime, direction, bruto)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (timestamp, direction, weight))
        mysql.connection.commit()
        session_id = cursor.lastrowid
        cursor.close()
        return jsonify({"id": session_id, "truck": "na", "bruto": weight}), 200

    # Handle "in"
    if direction == "in":
        cursor.execute("""
            SELECT id FROM transactions WHERE truck = %s AND direction = 'in' ORDER BY datetime DESC LIMIT 1
        """, (truck,))
        last_in_session = cursor.fetchone()

        if last_in_session and not force:
            return jsonify({"error": "Truck already weighed in, use force=true to overwrite"}), 400

        if last_in_session and force:
            query = """
                UPDATE transactions 
                SET datetime = %s, containers = %s, bruto = %s, produce = %s
                WHERE id = %s
            """
            containers_str = ",".join(containers_list)
            cursor.execute(query, (timestamp, containers_str, weight, produce, last_in_session[0]))
            mysql.connection.commit()
            return jsonify({"id": last_in_session[0], "truck": truck, "bruto": weight}), 200

        query = """
            INSERT INTO transactions (datetime, direction, truck, containers, bruto, produce)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        containers_str = ",".join(containers_list)
        cursor.execute(query, (timestamp, direction, truck, containers_str, weight, produce))
        mysql.connection.commit()
        session_id = cursor.lastrowid
        cursor.close()
        return jsonify({"id": session_id, "truck": truck, "bruto": weight}), 200

    # Handle "out"
    if direction == "out":
        cursor.execute("""
            SELECT id, bruto FROM transactions WHERE truck = %s AND direction = 'in' ORDER BY datetime DESC LIMIT 1
        """, (truck,))
        previous_session = cursor.fetchone()

        if not previous_session:
            return jsonify({"error": "'out' without 'in' is not allowed"}), 400

        previous_id, bruto = previous_session

        placeholders = ", ".join(["%s"] * len(containers_list))
        query = f"SELECT weight FROM containers_registered WHERE container_id IN ({placeholders})"
        cursor.execute(query, containers_list)
        container_weights = cursor.fetchall()
        containers = [cw[0] for cw in container_weights]
        neto = calculate_neto(bruto, weight, containers)

        query = """
            INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        containers_str = ",".join(containers_list)
        cursor.execute(query, (timestamp, direction, truck, containers_str, bruto, weight, neto, produce))
        session_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "id": session_id,
            "truck": truck,
            "bruto": bruto,
            "truckTara": weight,
            "neto": neto
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
            return jsonify({"error": "No file specified"}), 404
            
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
            return jsonify({"error": "Unsupported file format"}), 404

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
