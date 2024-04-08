import os
import requests
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from PIL import Image
import base64
import imghdr
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from Crypto.Util.Padding import unpad

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3', 'ogg', 'doc', 'docx'}

UNSPLASH_API_URL = 'https://source.unsplash.com/random'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USERNAME = ''#outlook mail and password
EMAIL_PASSWORD = ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_key():
    return get_random_bytes(16)

def encrypt_file(file_path, key):
    cipher = AES.new(key, AES.MODE_CBC)
    
    with open(file_path, 'rb') as file:
        plaintext = file.read()
    
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    filename_without_extension, extension = os.path.splitext(os.path.basename(file_path))
    encrypted_filename = filename_without_extension + '_encrypted' + extension
    encrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(encrypted_filename))
    with open(encrypted_file_path, 'wb') as encrypted_file:
        encrypted_file.write(cipher.iv + ciphertext)
    return encrypted_file_path

def fetch_random_image():
    response = requests.get(UNSPLASH_API_URL)
    if response.status_code == 200:
        return response.content
    else:
        return None
def retrieve_key_from_image(image_path):
    img = Image.open(image_path)
    key_str = ''
    for pixel_tuple in img.getdata():
        key_str += chr(pixel_tuple[0])
    key = base64.b64decode(key_str.encode('utf-8'))
    return key
def hide_key_in_image(image_data, key):
    img = Image.open(BytesIO(image_data))
    key_str = base64.b64encode(key).decode('utf-8')
    img.putdata(list(map(ord, key_str)))
    key_hidden_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'key_hidden_image.png')
    img.save(key_hidden_image_path)
    return key_hidden_image_path
def decrypt_file(encrypted_file_path, key):
    with open(encrypted_file_path, 'rb') as encrypted_file:
        data = encrypted_file.read()
    iv = data[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(data[AES.block_size:])
    decrypted_data = unpad(decrypted_data, AES.block_size)
    decrypted_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decrypted_' + os.path.basename(encrypted_file_path))
    with open(decrypted_file_path, 'wb') as decrypted_file:
        decrypted_file.write(decrypted_data)
    return decrypted_file_path

def send_email_with_attachments(recipient_email, subject, message_body, files):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message_body, 'plain'))
    for file_path in files:
        with open(file_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(file_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        msg.attach(part)
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, recipient_email, msg.as_string())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if request.form['option'] == 'encrypt':
                key = generate_key()
                encrypted_file_path = encrypt_file(file_path, key)
                random_image_data = fetch_random_image()
                if not random_image_data:
                    return "Failed to fetch random image"
                key_hidden_image_path = hide_key_in_image(random_image_data, key)
                recipient_email = request.form['recipient_email']
                subject = "Encrypted File and Key Image"
                message_body = "Please find the encrypted file and key image attached."
                files = [encrypted_file_path, key_hidden_image_path]
                send_email_with_attachments(recipient_email, subject, message_body, files)
                return "File encrypted successfully. Email sent with encrypted file and key image attachments."
            
            elif request.form['option'] == 'decrypt':
                key_image = request.files['key_image']
                if key_image and allowed_file(key_image.filename):
                    key_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(key_image.filename))
                    key_image.save(key_image_path)
                    
                    key = retrieve_key_from_image(key_image_path)
                    decrypted_file_path = decrypt_file(file_path, key)
                    recipient_email = request.form['recipient_email']
                    subject = "Decrypted File"
                    message_body = "Please find the decrypted file attached."
                    files = [decrypted_file_path]
                    send_email_with_attachments(recipient_email, subject, message_body, files)

                    return "File decrypted successfully. Email sent with decrypted file attachment."
                else:
                    return "Invalid key image"
            else:
                return "Invalid option"
        else:
            return "Invalid file format"
    
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=False)