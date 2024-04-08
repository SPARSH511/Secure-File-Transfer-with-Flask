# Secure File Transfer with Flask

This Flask application provides a secure method for encrypting and decrypting files, using AES encryption. It allows users to upload files, encrypt them, and send them via email. Additionally, users can decrypt files received via email.
This project utilizes 128 bit AES Encryption to encrypt audio, video and text files and use Image Steganography using Base64 encoding and LSB Technique to hide the key after encryption inside random images and facilitate secure file transfer.

## Features

- **File Encryption**: Upload files and encrypt them using AES encryption.
- **Email Integration**: Send encrypted files and key images via email for secure transfer.
- **File Decryption**: Decrypt files received via email using a key image.

## Prerequisites

Before running the application, make sure you have the following installed:

- Python (>= 3.6)
- Flask
- Pillow (PIL fork for image processing)
- pycryptodome (Python cryptography library)
- requests (for fetching random images)
- smtplib (for sending emails)

## Installation
1. Download the files on your computer. 
2. Set up your email configuration in the `app.py` file:
    EMAIL_USERNAME = '<your-email>' <br>
    EMAIL_PASSWORD = '<your-email-password>' <br>
3. Run the app.py by using an IDE or the command:
    python app.py
4. Open your web browser and go to http://localhost:5000 to access the application.
5. Choose whether you want to encrypt or decrypt a file, provide necessary details such as recipient email, and upload the file.
6. If encrypting, a key image will be generated and attached to the email along with the encrypted file. If decrypting, make sure to upload the key image received via email.

## Acknowledgments
This project was inspired by the need for a secure file transfer method.
Special thanks to the developers of Flask, Pillow, and pycryptodome for their excellent libraries.

