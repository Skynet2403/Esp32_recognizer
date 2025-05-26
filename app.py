from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "Servidor de reconocimiento facial activo."

@app.route('/analizar', methods=['POST'])
def analizar():
    print("Imagen recibida (simulada).")
    rostro_autorizado = True  # Aquí irá tu lógica con OpenCV

    return "autorizado" if rostro_autorizado else "denegado"

if __name__ == '__main__':
    app.run()
