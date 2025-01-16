from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.get_json()
    jsonBranch = event.get('ref') #'ref' is the JSON field containing the branch
    if jsonBranch and jsonBranch.startswith('refs/heads'):
        branchName = jsonBranch.split('/')[-1]
    else: 
        branchName = None # if 'ref' is not in the expected format or branch does not exist

    try:
        #running bash script with branchName as given arg, check for errors if exit!=0
        # subprocess.run(['./builder.sh', branchName], check=True)
        app.logger.info('docker exec host-container /home/ubuntu/GanShmuel/ganshmuelgreen/DevOps/builder.sh')
    except subprocess.CalledProcessError as e:
        print(f"Error running bash script: {e}")
    print(event)
    print(request)
    app.logger.info(str(event))
    app.logger.info(str(request))
    return jsonify({'message': 'Webhook received'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
