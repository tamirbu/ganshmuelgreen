from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import pytz
import os
import logging

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DATABASE')

# Initialize MySQL
mysql = MySQL(app)

@app.route('/health', methods=['GET'])
def health():
    try:
        # Try to connect to database and execute simple query
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        return "OK", 200
    except Exception as e:
        # If database connection fails
        print(f"Health check failed: {e}")
        return "Failure", 500
@app.route('/weight', methods=['GET'])
def get_weight():
    # Get query parameters
    from_date = request.args.get('from')
    to_date = request.args.get('to')
    filter_param = request.args.get('filter', 'in,out,none')

   def parse_date_range(from_date, to_date):
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
            raise ValueError("from_date must include time when provided.")
    else:
        raise ValueError("from_date is required and must include time.")

    # Parse to_date
    if to_date:
        to_date = parse_date_with_time(to_date)
        if to_date is None:
            raise ValueError("to_date must include time when provided.")
    else:
        raise ValueError("to_date is required and must include time.")

    # Check if to_date is earlier than from_date
    if to_date < from_date:
        raise ValueError("to_date cannot be earlier than from_date.")

    return from_date, to_date

    # Prepare the SQL query
    query = """
    SELECT id, direction, bruto, neto, produce, containers, truck
    FROM Transactions
    WHERE datetime BETWEEN %s AND %s
    AND direction IN ({})
    """.format(','.join(['%s'] * len(filter_param.split(','))))

    params = [from_date, to_date] + filter_param.split(',')

    try:
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute(query, params)
        transactions = cur.fetchall()

        result = []
        for t in transactions:
            transaction_dict = {
                "id": t['id'],
                "direction": t['direction'],
                "bruto": int(t['bruto']),  # Ensure it's an integer
                "neto": int(t['neto']) if t['neto'] is not None else "na",
                "produce": t['produce'],
                "containers": t['containers'].split(',') if t['containers'] else []
            }
            
            # Handle 'none' direction for containers without a truck
            if t['direction'] == 'none' and t['truck'] == 'na':
                transaction_dict["direction"] = "none"
            
            result.append(transaction_dict)

        return jsonify(result)

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

    finally:
        if cur:
            cur.close()

@app.route('/unknown', methods=['GET'])
def get_unknown_containers():
    try:
        cur = mysql.connection.cursor()
        
        # Query to find containers with unknown weight
        query = """
        SELECT DISTINCT container_id
        FROM Containers
        WHERE weight IS NULL OR weight = 0
        ORDER BY container_id
        """
        
        cur.execute(query)
        unknown_containers = [row[0] for row in cur.fetchall()]
        
        return jsonify(unknown_containers), 200

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

    finally:
        if cur:
            cur.close()

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
        # Query the database for the session
        cur = mysql.connection.cursor(dictionary=True)
        cur.execute("""
            SELECT id, truck, bruto, direction, truckTara, neto
            FROM Transactions
            WHERE id = %s
        """, (id,))
        
        session = cur.fetchone()
        cur.close()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        # Prepare the response
        response = {
            "id": session['id'],
            "truck": session['truck'] if session['truck'] else "na",
            "bruto": session['bruto']
        }
        
        # Add OUT-specific fields if the direction is 'out'
        if session['direction'] == 'out':
            response["truckTara"] = session['truckTara']
            response["neto"] = session['neto'] if session['neto'] is not None else "na"
        
        return jsonify(response)

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

if __name__ == '__main__':
    # Verify database connection
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.close()
            print("Successfully connected to MySQL database!")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
    
    app.run(host='0.0.0.0', port=5000)