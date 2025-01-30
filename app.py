from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("EMAIL_USERNAME")
SMTP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

def send_email(to_email, subject, body):
  try:
      # Create message
      message = MIMEMultipart()
      message["From"] = SMTP_USERNAME
      message["To"] = to_email
      message["Subject"] = subject

      # Add body to email
      message.attach(MIMEText(body, "plain"))

      # Create SMTP session
      with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
          server.starttls()
          server.login(SMTP_USERNAME, SMTP_PASSWORD)
          server.send_message(message)

      return True
  except Exception as e:
      print(f"Error sending email: {str(e)}")
      return False

@app.route("/")
def home():
  return "Email Service is Running!"

@app.route("/send-email", methods=["POST"])
def send_email_endpoint():
  data = request.get_json()

  # Validate required fields
  required_fields = ["to_email", "subject", "body"]
  for field in required_fields:
      if field not in data:
          return jsonify({"error": f"Missing required field: {field}"}), 400

  # Send email
  success = send_email(
      data["to_email"],
      data["subject"],
      data["body"]
  )

  if success:
      return jsonify({"message": "Email sent successfully"}), 200
  else:
      return jsonify({"error": "Failed to send email"}), 500

if __name__ == "__main__":
  app.run(debug=True)