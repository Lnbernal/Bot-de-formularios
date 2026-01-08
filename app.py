from flask import Flask, render_template, request
from bot import ejecutar_bot

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("formulario.html")

@app.route("/ejecutar", methods=["POST"])
def ejecutar():
    numero_fijo = request.form["numero_fijo"]
    cantidad = int(request.form["cantidad"])

    ejecutar_bot(
        max_respuestas=cantidad,
        numero_fijo=numero_fijo
    )

    return "Bot ejecutado correctamente"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
