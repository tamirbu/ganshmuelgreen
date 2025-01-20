# send_email.py
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart






def send_email(message, to_email):
    # Replace with your actual email credentials
    from_email = "ganshmuelgreen1@gmail.com"
    from_password = "kujy lpfr xqsy tfvz"

    # Set up the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Subject: Custom Message'

    # Add message body
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Set up the server (e.g., using Gmail SMTP server)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure connection
        server.login(from_email, from_password)  # Login with your email and password
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)  # Send email
        server.quit()  # Close the connection
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Send an email with a message.")
    parser.add_argument('message', type=str, help="The message to send in the email.")
    parser.add_argument('email', type=str, help="The recipient email address.")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Send email with the message and email address provided
    send_email(args.message, args.email)

if __name__ == '__main__':
    main()
