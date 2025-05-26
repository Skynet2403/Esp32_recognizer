from flask import Flask, request
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Simula que ya tienes una "base de rostros" autorizados
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/')
def index():
    return "Servidor activo para reconocimiento facial."

@app.route('/analizar', methods=['POST'])
def analizar():
    data = request.get_json()
    if not data or 'imagen' not in data:
        return "formato inválido", 400

    try:
        # Decodifica imagen base64 a matriz OpenCV
        img_data = base64.b64decode(data['imagen'])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Detecta rostros
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rostros = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(rostros) > 0:
            print("Rostro detectado")
            return "autorizado"
        else:
            print("Sin rostro")
            return "denegado"
    except Exception as e:
        print("Error al procesar la imagen:", e)
        return "error interno", 500

if __name__ == '__main__':
    app.run()
