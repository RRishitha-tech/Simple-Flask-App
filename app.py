from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sas_url = "https://project3webapp.blob.core.windows.net/blob?sp=racwdli&st=2024-08-19T21:52:02Z&se=2024-08-20T05:52:02Z&sv=2022-11-02&sr=c&sig=RExUI2WXTMZct%2Bviqy35R1G%2FgMFPy1jCObo%2BunLPwF8%3D"
blob_service_client = BlobServiceClient(account_url=sas_url)

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_blob_storage(file_path, blob_name):
    try:
        blob_client = blob_service_client.get_blob_client(container="blob", blob=blob_name)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)

        print(f"File {blob_name} uploaded to Blob storage successfully.")
    except Exception as e:
        print(f"Error: {e}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Upload the file to Azure Blob Storage
            upload_to_blob_storage(filepath, filename)
            
            flash(f"File {filename} uploaded successfully.")
            return redirect(request.url)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
