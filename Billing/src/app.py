from flask import Flask, request, jsonify
import mysql.connector
import os

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


@app.route("/truck/<id>", methods=["PUT"])
def update_truck(id):
    """
    Updates or creates a truck entry in the database.

    Parameters:
        id (str): The truck ID provided in the URL.
        JSON body:
            - provider_id (int): The provider ID to associate with the truck.

    Returns:
        JSON response:
            - On success (200): {"id": truck_id, "provider_id": provider_id}
            - On missing provider_id in request body (400): {"error": "Missing provider_id"}
            - On non-existent provider_id (404): {"error": "Provider ID does not exist"}
            - On server/database error (500): {"error": <error_message>}
    """
    # Parse the JSON body of the request
    data = request.get_json()

    # Validate that provider_id is present in the request body
    if not data or "provider_id" not in data:
        return jsonify({"error": "Missing provider_id"}), 400

    provider_id = data["provider_id"]

    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the provider exists in the Provider table
        cursor.execute("SELECT COUNT(*) FROM Provider WHERE id = %s", (provider_id,))
        provider_exists = cursor.fetchone()[0]

        # If the provider does not exist, return a 404 error
        if not provider_exists:
            return jsonify({"error": "Provider ID does not exist"}), 404

        # Check if the truck exists in the Trucks table
        cursor.execute("SELECT COUNT(*) FROM Trucks WHERE id = %s", (id,))
        truck_exists = cursor.fetchone()[0]

        if truck_exists:
            # Update the existing truck's provider_id
            query = "UPDATE Trucks SET provider_id = %s WHERE id = %s"
            cursor.execute(query, (provider_id, id))
        else:
            # Insert a new truck record
            query = "INSERT INTO Trucks (id, provider_id) VALUES (%s, %s)"
            cursor.execute(query, (id, provider_id))

        # Commit the transaction to the database
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        # Return a success response
        return jsonify({"id": id, "provider_id": provider_id}), 200

    except mysql.connector.Error as err:
        # Handle database errors and return an error response
        return jsonify({"error": str(err)}), 500


@app.route("/truck/<id>", methods=["GET"])
def get_truck(id):
    """
    Checks if a truck with the given ID exists in the database.

    Parameters:
        id (str): The truck ID provided in the URL.

    Returns:
        JSON response:
            - On success (200): {"message": "Truck exists", "id": truck_id}
            - On not found (404): {"error": "Truck not found"}
    """
    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the truck exists in the Trucks table
        query = "SELECT COUNT(*) FROM Trucks WHERE id = %s"
        cursor.execute(query, (id,))
        truck_exists = cursor.fetchone()[0]

        # If the truck exists, return success
        if truck_exists:
            cursor.close()
            conn.close()
            return jsonify({"message": "Truck exists", "id": id}), 200

        # If the truck does not exist, return not found
        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "Truck not found"}), 404

    except mysql.connector.Error as err:
        # Handle database errors
        return jsonify({"error": str(err)}), 500

@app.route("/provider/<int:id>", methods=["PUT"])
def update_provider(id):
    conn = None
    try:
        # Get JSON data for provider update
        data = request.get_json()
        new_name = data.get("name")
        if new_name is None:
            return jsonify({"error": "Name is required"}), 400

        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check existing provider by ID
        cursor.execute("SELECT name FROM Provider WHERE id = %s", (id,))
        existing_provider = cursor.fetchone()

        if existing_provider:
            # If the provider exists, update the name
            cursor.execute("UPDATE Provider SET name = %s WHERE id = %s", (new_name, id))
            conn.commit()
            return jsonify({
                "message": "Provider updated",
                "id": id,
                "previous_name": existing_provider[0],
                "new_name": new_name
            }), 200  # Return 200 OK for an update

        else:
            # If the provider doesn't exist, insert a new provider
            cursor.execute("INSERT INTO Provider (id, name) VALUES (%s, %s)", (id, new_name))
            conn.commit()
            return jsonify({
                "message": "Provider created",
                "id": id,
                "name": new_name
            }), 201  # Return 201 Created for new provider

    except Exception as e:
        # Handle any errors
        if conn:
            conn.rollback()
        return jsonify({
            "error": "Operation failed",
            "details": str(e)
        }), 500

    finally:
        # Ensure resources are properly closed
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conn:
            conn.close()

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
