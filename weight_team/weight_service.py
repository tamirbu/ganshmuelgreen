from flask import Flask, jsonify
from flask_mysqldb import MySQL
import os

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