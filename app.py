from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session
import os
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Ensure the 'uploads' folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email Configuration (Gmail in this example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'digpalsingh9240@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'cegilrmtnfvrmiig'  # Replace with your email password
mail = Mail(app)

# Hardcoded credentials
CREDS = {'Admin': 'Admin001',
         'Alen': 'alen123',
         'yash': 'yash123',
         'amar': 'amar123',
         'mohammed': 'mohammed123'}

# Route for the login page
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if username in CREDS:
            if password == CREDS[username]:
                session['user'] = username
                session['email'] = email  # Store email in session
                # Generate and send OTP
                otp = generate_otp()
                session['otp'] = otp
                send_otp_email(email, otp)  # Send OTP to the entered email
                return redirect(url_for('generate_otp_page'))
            else:
                return 'Invalid credentials, please try again.'
    return render_template('login.html')

# Function to generate OTP
def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

# Function to send OTP to email
def send_otp_email(user_email, otp):
    msg = Message("Your OTP Code", sender="your_email@gmail.com", recipients=[user_email])
    msg.body = f"Your OTP code is {otp}. Please use this code to complete your login."
    mail.send(msg)

# Route for the OTP page
@app.route('/generate_otp')
def generate_otp_page():
    return render_template('otp.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form['otp']
    generated_otp = session.get('otp')

    if entered_otp == generated_otp:
        return redirect(url_for('index'))
    else:
        return 'Invalid OTP, please try again.'

# Route for the homepage (after login)
@app.route('/index')
def index():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' in session:
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        
        os.makedirs(f"{app.config['UPLOAD_FOLDER']}/{session['user']}", exist_ok=True)
        
        filename = os.path.join(f"{app.config['UPLOAD_FOLDER']}/{session['user']}", file.filename)
        file.save(filename)
        return "<h3 style = 'font-size:20px; color:green' align = 'center'>File uploaded successfully!</h3>"
    return redirect(url_for('login'))

# Route to view uploaded files
@app.route('/uploads')
def list_files():
    if 'user' in session:
        try:
            files = os.listdir(f"{app.config['UPLOAD_FOLDER']}/{session['user']}")
        except FileNotFoundError:
            files = ["no file found."]
        return render_template('uploads.html', files=files)
        
    return redirect(url_for('login'))

# Route to handle file downloads
@app.route('/download/<filename>')
def download_file(filename):
    if 'user' in session:
        return send_from_directory(f"{app.config['UPLOAD_FOLDER']}/{session['user']}", filename)
    return redirect(url_for('login'))

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
