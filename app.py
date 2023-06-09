import os
import openai
from flask import Flask, request, render_template, send_file
from pydub import AudioSegment
from gtts import gTTS
from flask import jsonify
from flask import send_from_directory
import uuid
from dotenv import load_dotenv
import json
from firebase_admin import credentials, storage
import firebase_admin
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()

firebase_credentials = {
    "type": os.environ["FIREBASE_TYPE"],
    "project_id": os.environ["FIREBASE_PROJECT_ID"],
    "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
    "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace('\\n', '\n'),
    "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
    "client_id": os.environ["FIREBASE_CLIENT_ID"],
    "auth_uri": os.environ["FIREBASE_AUTH_URI"],
    "token_uri": os.environ["FIREBASE_TOKEN_URI"],
    "auth_provider_x509_cert_url": os.environ["FIREBASE_AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
}

cred = credentials.Certificate(firebase_credentials)
firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': os.environ["FIREBASE_STORAGE_BUCKET"],
})

firebase_config = {
    "apiKey": os.environ["FIREBASE_API_KEY"],
    "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
    "databaseURL": os.environ["FIREBASE_DATABASE_URL"],
    "projectId": os.environ["FIREBASE_PROJECT_ID"],
    "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": os.environ["FIREBASE_APP_ID"],
    "measurementId": os.environ["FIREBASE_MEASUREMENT_ID"],
}

openai.api_key = os.environ["OPENAI_API_KEY"]

# Configure PyDub to use the correct paths for FFmpeg and FFprobe
AudioSegment.converter = os.environ.get('FFMPEG_PATH', 'ffmpeg')
AudioSegment.ffmpeg = os.environ.get('FFMPEG_PATH', 'ffmpeg')
AudioSegment.ffprobe = os.environ.get('FFPROBE_PATH', 'ffprobe')

# Replace the global messages variable with a dictionary to store multiple chat sessions
chat_sessions = {}

@app.route("/firebase_config", methods=["GET"])
def firebase_config():
    config = {
        "apiKey": os.environ["FIREBASE_API_KEY"],
        "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
        "databaseURL": os.environ["FIREBASE_DATABASE_URL"],
        "projectId": os.environ["FIREBASE_PROJECT_ID"],
        "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
        "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
        "appId": os.environ["FIREBASE_APP_ID"],
        "measurementId": os.environ["FIREBASE_MEASUREMENT_ID"],
    }
    return jsonify(config)

# Generate a new chat session and return the session ID
@app.route("/new_session", methods=["GET"])
def new_session():
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = [
        {
            "role": "system",
            "content": "You are a helpful ai assistant, all responses should be less than 75 words.",
        }
    ]
    return jsonify({"session_id": session_id})

def convert_audio_to_wav(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="wav")

@app.route("/", methods=["GET"])
def landing():
    return render_template("landing_page.html")

@app.route("/app", methods=["GET"])
def index():
    return render_template("index.html")

# Add this new route for index.html
@app.route('/index')
def serve_index():
    return render_template('index.html')

# Create audio_files directory if it doesn't exist
if not os.path.exists('audio_files'):
    os.makedirs('audio_files', exist_ok=True)


@app.route("/chat/<session_id>", methods=["POST"])
def chat(session_id):
    if session_id not in chat_sessions:
        return jsonify({"status": "error", "message": "Chat session not found"}), 404

    messages = chat_sessions[session_id]
    audio_file = request.files["audio"]
    converted_audio_file = "converted_audio.wav"
    convert_audio_to_wav(audio_file, converted_audio_file)

    transcription = openai.Audio.transcribe(
        "whisper-1", open(converted_audio_file, "rb"))
    messages.append({"role": "user", "content": transcription["text"]})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages)

    messages.append(
        {"role": "assistant", "content": completion.choices[0].message["content"]})

    tts = gTTS(text=completion.choices[0].message["content"], lang='en')
    audio_filename = f'response_{len(messages)//2}.mp3'
    tts.save(f'audio_files/{audio_filename}')

    # Return transcriptions and audio file as JSON
    return jsonify({
        "user_text": transcription["text"],
        "assistant_text": completion.choices[0].message["content"],
        "assistant_audio": f"/audio/{audio_filename}"
    })

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('audio_files', filename)

if __name__ == "__main__":
    app.run(debug=True)
