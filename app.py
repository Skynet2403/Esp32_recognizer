from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, storage
import face_recognition
import cv2
import numpy as np
import base64
import os
from datetime import datetime
import json

app = Flask(__name__)

# Inicializar Firebase desde variable de entorno
cred_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'esp32-face-lock.appspot.com'  # REEMPLAZA si es necesario
})
bucket = storage.bucket()

@app.route('/')
def index():
    return "Servidor activo con Firebase."

@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    if not data or 'imagen' not in data or 'nombre' not in data:
        return "datos inválidos", 400

    try:
        img_data = base64.b64decode(data['imagen'])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{data['nombre']}_{timestamp}.jpg"

        blob = bucket.blob(f"rostros/{filename}")
        blob.upload_from_string(img_data, content_type='image/jpeg')
        return "rostro guardado"
    except Exception as e:
        print("Error al guardar:", e)
        return "error", 500

@app.route('/analizar', methods=['POST'])
def analizar():
    data = request.get_json()
    if not data or 'imagen' not in data:
        return "imagen inválida", 400

    try:
        img_data = base64.b64decode(data['imagen'])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)

        if not encodings:
            return "sin rostro"

        current_encoding = encodings[0]

        blobs = list(bucket.list_blobs(prefix="rostros/"))
        for blob in blobs:
            if not blob.name.endswith(".jpg"):
                continue
            local_path = f"temp_{os.path.basename(blob.name)}"
            blob.download_to_filename(local_path)

            known_img = face_recognition.load_image_file(local_path)
            known_enc = face_recognition.face_encodings(known_img)
            os.remove(local_path)
            if known_enc and face_recognition.compare_faces([known_enc[0]], current_encoding)[0]:
                return "autorizado"

        return "denegado"
    except Exception as e:
        print("Error en análisis:", e)
        return "error", 500

if __name__ == '__main__':
    app.run(debug=True)
