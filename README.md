<h1>Flask Cloud Storage App with Google Cloud Storage and Email OTP</h1>
 <h2>Overview</h2>
    <p>This Flask application provides secure cloud storage functionality, integrating Google Cloud Storage to handle file uploads, downloads, and deletions. The app includes file encryption and decryption features, and files can be shared via email or a generated share link.</p>
        <h2>Features</h2>
    <ul>
        <li>User authentication with OTP-based email verification</li>
        <li>File upload with encryption (using either a custom key or default key)</li>
        <li>Encrypted file download with custom key decryption</li>
        <li>Google Cloud Storage integration for file management</li>
        <li>Share files via email or generated link with read/write permissions</li>
        <li>File deletion after providing the correct encryption key</li>
    </ul>

    <h2>Requirements</h2>
    <ul>
        <li>Python 3.7 or higher</li>
        <li>Flask</li>
        <li>cryptography</li>
        <li>flask-mail</li>
        <li>google-cloud-storage</li>
        <li>A Google Cloud project with Google Cloud Storage enabled</li>
        <li>A service account JSON file from Google Cloud with access to the storage bucket</li>
    </ul>

    <h2>Setup and Installation</h2>
    <ol>
        <li>Clone the repository:</li>
        <pre><code>git clone &lt;repository_url&gt;</code></pre>

        <li>Navigate to the project directory:</li>
        <pre><code>cd flask-cloud-storage-app</code></pre>

        <li>Create and activate a virtual environment:</li>
        <pre><code>
python -m venv venv
source venv/bin/activate  <!-- For Linux/macOS -->
venv\Scripts\activate     <!-- For Windows -->
</code></pre>

        <li>Install the required packages:</li>
        <pre><code>pip install -r requirements.txt</code></pre>

        <li>Set up your Google Cloud credentials:</li>
        <ol>
            <li>Create a service account on Google Cloud and download the JSON key file.</li>
            <li>Replace <code>C:/Users/yash5/Desktop/cloud_project/file/file-storage-app-438915-c95404402e86.json</code> in the code with the path to your JSON key file.</li>
            <li>Set the Google Cloud Storage bucket name as <code>bucket_name</code>.</li>
        </ol>

        <li>Configure your Gmail settings in the code:</li>
        <pre><code>
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password' <!-- Ensure less secure apps are enabled in Gmail -->
</code></pre>

        <li>Run the application:</li>
        <pre><code>python app.py</code></pre>

        <li>Access the app in your browser at <a href="http://localhost:5000" target="_blank">http://localhost:5000</a>.</li>
    </ol>

    <h2>Usage</h2>
    <ol>
        <li>Log in with a valid username and password. After login, you'll be prompted to enter an OTP sent to your email.</li>
        <li>Upload files with an option to encrypt them with a custom key. Files are stored in Google Cloud Storage in an encrypted format.</li>
        <li>Download files by providing the correct decryption key.</li>
        <li>Share files via email or link, specifying read/write permissions.</li>
        <li>Delete files from cloud storage after confirming with the correct encryption key.</li>
    </ol>

    <h2>File Structure</h2>
    <pre>
app.py              # Main application file
templates/          # HTML templates for the web interface
static/             # Static files (e.g., CSS, JS)
requirements.txt    # List of dependencies
</pre>

    <h2>Security Notes</h2>
    <ul>
        <li>Ensure that the Google Cloud service account JSON file is kept secure and not committed to any public repositories.</li>
        <li>Consider using environment variables for sensitive configurations like email credentials.</li>
    </ul>

    <h2>Contact</h2>
    <p>For questions or support, please reach out to the project maintainer.</p>


