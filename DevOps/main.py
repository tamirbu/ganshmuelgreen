from flask import Flask, request, jsonify
from email.mime.text import MIMEText
import smtplib
import subprocess
app = Flask(__name__)
SMTP_SERVER = 'smtp.gmail.com' # e.g., smtp.gmail.com for Gmail
SMTP_PORT = 587
SMTP_USER = 'ganshmuelgreen1@gmail.com' # your email account for sending emails
SMTP_PASSWORD = 'devopsgreen' # your email account password or app password

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
            print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Check if the event is for the 'main' branch (or any other branch you care about)
    if data['ref'] == ['refs/heads/main', 'refs/heads/billing', 'refs/heads/weight']: # Only trigger for pushes to the main branch
        # Extract the committer's email
        pusher_email = data['pusher']['email']
        commit_message = data['head_commit']['message']
        # Send the email to the pusher (the person who pushed the changes)
        send_email(
            to_email=pusher_email,
            subject="Your recent push to GitHub Repository",
            body=f"Hi {data['pusher']['name']},\n\nYou recently pushed the following commit to the repository:\n\nCommit message: {commit_message}\n\nWe are testing your update!"
)
        return "Email sent", 200
    else:
        return "Not a push to tracked branches branch", 200
if __name__ == '__main__':
    app.run(debug=True, port=5000)
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
        app.logger.error(f"ERROR: {e}")
    app.logger.info(f"Building: {branchName}")
    app.logger.info(str(request))
    return jsonify({'message': 'Webhook received'}), 200
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
