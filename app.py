from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session, jsonify, make_response,flash
from cryptography.fernet import Fernet
import os
import random
import string
from flask_mail import Mail, Message 
from werkzeug.utils import secure_filename
import base64






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
         'yashraj': 'yash123',
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

def encrypt_file(file_data, custom_key=None):
    if custom_key:
        # Ensure custom_key is 32 bytes long
        if isinstance(custom_key, str):
            custom_key = custom_key.ljust(32)[:32].encode()  # Pad or truncate to 32 bytes
        elif isinstance(custom_key, bytes):
            custom_key = custom_key.ljust(32)[:32]
        custom_key = base64.urlsafe_b64encode(custom_key)
    else:
        # Use the default key
        custom_key = Fernet.generate_key()
    
    fernet = Fernet(custom_key)
    encrypted_data = fernet.encrypt(file_data)
    return encrypted_data, custom_key

def decrypt_file(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user' in session:
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        # Prompt user for encryption option
        encrypt_option = request.form.get('encrypt_option')  # 'custom' or 'default'
        encryption_key = request.form.get('encryption_key') if encrypt_option == 'custom' else None
        os.makedirs(f"{app.config['UPLOAD_FOLDER']}/{session['user']}", exist_ok=True)
        filename = secure_filename(file.filename)
        file_path = os.path.join(f"{app.config['UPLOAD_FOLDER']}/{session['user']}", filename)

        # Encrypt file data
        file_data = file.read()
        encrypted_data, custom_key = encrypt_file(file_data, encryption_key)
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)

        # Save key if 'custom' was chosen
        if encrypt_option == 'custom':
            session['custom_key'] = custom_key.decode()
            print(session['custom_key'])

        flash("File uploaded and encrypted successfully!", "success")
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    if 'user' in session:
        if request.method == 'POST':
            # Get the custom key from the form submission
            custom_key = request.form['custom_key']
            if custom_key:
                custom_key = custom_key.ljust(32)[:32].encode()
                custom_key = base64.urlsafe_b64encode(custom_key)
            else:
                custom_key = session.get('custom_key').encode()

            # Read the encrypted file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['user'], filename)
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            try:
                # Decrypt the file using the provided key
                decrypted_data = decrypt_file(encrypted_data, custom_key)
                response = make_response(decrypted_data)
                response.headers['Content-Disposition'] = f'attachment; filename={filename}'
                return response
            except Exception as e:
                return f"Error during decryption: {str(e)}"
        return render_template('download_prompt.html', filename=filename)
    return redirect(url_for('login'))




#download uploaded files
@app.route('/uploaded_files')
def list_files():
    if 'user' in session:
        try:
            files = os.listdir(f"{app.config['UPLOAD_FOLDER']}/{session['user']}")
        except FileNotFoundError:
            files = ["no file found."]
        return render_template('uploaded_files.html', files=files)
        
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
