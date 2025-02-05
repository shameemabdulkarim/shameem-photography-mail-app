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
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://your-photography-site.com", #To be changed after deploying the photography app
                "http://localhost:3000" ,# For development
                "http://127.0.0.1:5000"
            ]
        }
    }
)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("EMAIL_USERNAME")
SMTP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# Middleware to verify API key
def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key and api_key == os.getenv('API_KEY'):
            return view_function(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

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
@require_api_key
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