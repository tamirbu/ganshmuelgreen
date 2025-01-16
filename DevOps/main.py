from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.get_json()
    jsonBranch = event.get('ref') #'ref' is the JSON field containing the branch
    if jsonBranch and jsonBranch.startswith('refs/heads'):
        branchName = jsonBranch.split('/')[-1]
    else: 
        branchName = None # if 'ref' is not in the expected format or branch does not exist
        
    contInit(branchName)
    print(event)
    print(request)
    app.logger.info(str(event))
    app.logger.info(str(request))
    return jsonify({'message': 'Webhook received'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
