from flask import Flask, request, jsonify
from email.mime.text import MIMEText
import smtplib
import subprocess
app = Flask(__name__)



mail_dict = {
    'tomermaas': 'tomermaas@gmail.com', 'levi3259': 'cl6724259@gmail.com', 'mikoga': 'mikoga89@gmail.com',
    'eitanp214': 'eitanp214@gmail.com', 'tamirbu': 'tamirbuch@gmail.com', 'ChenCohen123': 'chencohen812@gmail.com',
    'EsterOvrani': 'Ester.Ovrani@gmail.com', 'aviv-peten': 'avivpeten123@gmail.com',
    'sariGolombeck': 'sara.beck.dev@gmail.com', 'TomerFeiler': 'tomermfeiler@gmail.com'}

#!!! if a change is made in main.py (which can happen because because of 'git pull') 
# then the main.py restarts and it restarts up the prod environment.
# therefore - leave this commented !!! 
# try:
#     subprocess.run(['./prodStart.sh'])
# except Exception as e:
# # except subprocess.CalledProcessError as e:
#     app.logger.error("Error starting productions")
#     app.logger.error(f"ERROR: {e}")


@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.get_json()
    jsonBranch = event.get('ref') #'ref' is the JSON field containing the branch
    jsonMail = event.get('sender', {}).get('login', 'Unknown user')
    pusher_email = mail_dict.get(jsonMail, 'Unknown Email')
    
    
    if jsonBranch and jsonBranch.startswith('refs/heads'):
        branchName = jsonBranch.split('/')[-1]
    else:
        return "Bad request: branch not found", 400
    try:
        app.logger.info(f"Building: {branchName}")
        subprocess.run(['./builder.sh', branchName, pusher_email], check=True)
    except subprocess.CalledProcessError as e:
        app.logger.error(f"ERROR: {e}")
        return f'Server Error - cannot build for branch {branchName}', 500
    
    return jsonify({'message': 'Webhook received'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
