from flask import Flask, request, render_template
from bot_forms import ejecutar_bot
import threading
import os

app = Flask(__name__)

@app.route("/ejecutar", methods=["GET", "POST"])
def ejecutar():
    mensaje = None
    cantidad = 6
    numero_fijo = "101"
    estado_actual = None   # ← RENOMBRADO

    # leer estado si existe
    if os.path.exists("estado.txt"):
        with open("estado.txt", encoding="utf-8") as f:
            estado_actual = f.read().strip()

    if request.method == "POST":
        # borrar estado anterior
        if os.path.exists("estado.txt"):
            os.remove("estado.txt")

        cantidad = int(request.form.get("cantidad"))
        numero_fijo = request.form.get("numero_fijo")

        hilo = threading.Thread(
            target=ejecutar_bot,
            args=(cantidad, numero_fijo)
        )
        hilo.start()

        mensaje = f"Bot ejecutándose ({cantidad} respuestas, número {numero_fijo})"

    return render_template(
        "formulario.html",
        mensaje=mensaje,
        estado=estado_actual,   # ← aquí se pasa al HTML
        cantidad=cantidad,
        numero_fijo=numero_fijo
    )


@app.route("/estado")
def estado_api():
    if os.path.exists("estado.txt"):
        with open("estado.txt", encoding="utf-8") as f:
            return f.read().strip()
    return "EJECUTANDO"


@app.route("/")
def home():
    return "API Playwright activa"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
