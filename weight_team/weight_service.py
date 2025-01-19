
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
    try:
        weight = float(weight)
        if unit.lower() == 'lbs':
            return int(weight * 0.453592)
        return int(weight)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid weight value: {weight}")

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

@app.route('/health', methods=['GET'])
def health() -> tuple:
    """Health check endpoint"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        return "OK", 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return "Failure", 500

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
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.close()
            print("Successfully connected to MySQL database!")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
    
    app.run(host='0.0.0.0', port=5000)