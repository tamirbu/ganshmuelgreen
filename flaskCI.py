from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.get_json()

    return jsonify({'message': 'Webhook received'}), 200
