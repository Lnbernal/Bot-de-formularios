from flask import Flask, request, render_template
from bot_forms import ejecutar_bot
import threading

app = Flask(__name__)

@app.route("/ejecutar", methods=["GET", "POST"])
def ejecutar():
    mensaje = None
    cantidad = 6
    numero_fijo = "101"

    if request.method == "POST":
        cantidad = int(request.form.get("cantidad", 6))
        numero_fijo = request.form.get("numero_fijo", "101")

        hilo = threading.Thread(
            target=ejecutar_bot,
            args=(cantidad, numero_fijo)
        )
        hilo.start()

        mensaje = f"Bot ejecutándose ({cantidad} respuestas, número {numero_fijo})"

    return render_template(
        "formulario.html",
        mensaje=mensaje,
        cantidad=cantidad,
        numero_fijo=numero_fijo
    )


@app.route("/")
def home():
    return "API Playwright activa"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
