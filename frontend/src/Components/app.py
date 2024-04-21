from flask import Flask, send_from_directory
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('static', 'faceRecognition.js')

@app.route('/run-facial-recognition')
def run_facial_recognition():
    try:
        print("Calling script")
        subprocess.run(['python', r'C:\Users\91948\OneDrive\Desktop\FaceRecognition\facerecog.py'], check=True)
        return 'Facial recognition script executed successfully!', 200, {'Access-Control-Allow-Origin': '*'}
    except subprocess.CalledProcessError as e:
        print(e)
        return 'Error executing facial recognition script', 500, {'Access-Control-Allow-Origin': '*'}

if __name__ == '__main__':
    app.run(debug=True)