from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.get_json()
    print(event)
    print(request)
    return jsonify({'message': 'Webhook received'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
