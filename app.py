from flask import Flask, request, render_template, send_from_directory, redirect, url_for, session, jsonify, make_response,flash
from cryptography.fernet import Fernet
import os
import random
import string
from flask_mail import Mail, Message 
from werkzeug.utils import secure_filename
import base64
from google.cloud import storage # Adding Google Cloud Storage
# import io # For handling file streams



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management


# Google Cloud Configuration
# Modidify the path to the location of your .json service_account_file

storage_client = storage.Client.from_service_account_json("C:/Users/yash5/Desktop/cloud_project/file/file-storage-app-438915-c95404402e86.json")
bucket_name = 'storage_one_1'
bucket = storage_client.bucket(bucket_name)

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
         'mohamed': 'mohamed123'}

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

        # Encrypt file data
        file_data = file.read()
        encrypted_data, custom_key = encrypt_file(file_data, encryption_key)

        # Upload encrypted data to Google Cloud Storage
        blob = bucket.blob(f"{session['user']}/{secure_filename(file.filename)}")
        blob.upload_from_string(encrypted_data)

        # Save key if 'custom' was chosen
        if encrypt_option == 'custom':
            session['custom_key'] = custom_key.decode()

        flash("File uploaded and encrypted successfully!", "success")
        return redirect(url_for('index'))
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

            # Downlaod the encrypted file from Google Cloud Storage
            blob = bucket.blob(f"{session['user']}/{filename}")
            encrypted_data = blob.download_as_bytes()
            
            
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
def uploaded_files():
    if 'user' in session:
        blobs = bucket.list_blobs(prefix=f"{session['user']}/")
        files = [blob.name.split('/')[-1] for blob in blobs]
        return render_template('uploaded_files.html', files=files)
        
    return redirect(url_for('login'))




@app.route('/delete', methods=['POST'])
def delete_file():
    if 'user' in session:
        filename = request.form['filename']
        deletion_key = request.form['deletion_key']

        # Retrieve the stored key for this file
        stored_key = session.get('custom_key', '')

        # Ensure the key is in the correct format
        if deletion_key:
            deletion_key = deletion_key.ljust(32)[:32].encode()
            deletion_key = base64.urlsafe_b64encode(deletion_key)

        if deletion_key.decode() == stored_key:
            # Deleting file from Google Cloud Storage
            blob_path = f"{session['user']}/{filename}"  # User-specific path in the bucket
            blob = bucket.blob(blob_path)
            
            if blob.exists():
                blob.delete() # Deletes the file from the cloud
                flash(f"File '{filename}' deleted from cloud storage!", "success")
            else:
                flash(f"File '{filename}' not found in cloud storage.", "danger")
        else:
            flash("Incorrect key. File not deleted.", "danger")

        return redirect(url_for('uploaded_files'))
    return redirect(url_for('login'))




@app.route('/view/<filename>', methods=['POST'])
def view_file(filename):
    if 'user' in session:
        custom_key = request.form['custom_key']
        if custom_key:
            custom_key = custom_key.ljust(32)[:32].encode()
            custom_key = base64.urlsafe_b64encode(custom_key)

        # Retrieve the stored key for this file
        stored_key = session.get('custom_key', '')

        if custom_key.decode() == stored_key:
            
            # Getting the file from Google Cloud Storage
            blob_path = f"{session['user']}/{filename}"
            blob = bucket.blob(blob_path)

            if blob.exists():
                encrypted_data = blob.download_as_bytes()  # Download encrypted data from cloud
                try:
                    decrypted_data = decrypt_file(encrypted_data, custom_key)  # Decrypt file
                    return decrypted_data  # Return decrypted data to be displayed
                except Exception as e:
                    flash("Error during decryption.", "danger")
                    return redirect(url_for('uploaded_files'))
            else:
                flash("File not found in cloud storage.", "danger")
                return redirect(url_for('uploaded_files'))
            
        else:
            flash("Incorrect key. File not opened.", "danger")
            return redirect(url_for('uploaded_files'))
    return redirect(url_for('login'))






@app.route('/decrypt/<filename>', methods=['POST'])
def decrypt_for_sharing(filename):
    if 'user' in session:
        data = request.get_json()
        custom_key = data['custom_key']
        try:
            if custom_key:
                custom_key = custom_key.ljust(32)[:32].encode()
                custom_key = base64.urlsafe_b64encode(custom_key)
            else:
                custom_key = session.get('custom_key').encode()

            # Download the encrypted file
            blob = bucket.blob(f"{session['user']}/{filename}")
            encrypted_data = blob.download_as_bytes()
            
            # Decrypt the file using the provided key
            decrypt_file(encrypted_data, custom_key)  # Decrypt to verify the key

            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'User not logged in'})

@app.route('/share/email', methods=['POST'])
def share_via_email():
    if 'user' in session:
        data = request.get_json()
        file_name = data['fileName']
        permission = data['permission']
        recipient_email = data['email']

        # Generate share link
        link = url_for('download_file', filename=file_name, _external=True)

        # Send email
        msg = Message("File Share", sender="your_email@gmail.com", recipients=[recipient_email])
        msg.body = f"You have been given {permission} access to the file '{file_name}'.\nAccess it here: {link}"
        mail.send(msg)
        
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'User not logged in'})

@app.route('/share/link', methods=['POST'])
def generate_share_link():
    if 'user' in session:
        data = request.get_json()
        file_name = data['fileName']
        permission = data['permission']
        
        # Generate share link
        link = url_for('download_file', filename=file_name, _external=True)
        return jsonify({'success': True, 'link': link})
    return jsonify({'success': False, 'error': 'User not logged in'})










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
