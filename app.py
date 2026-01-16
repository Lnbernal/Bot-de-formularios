from flask import Flask, request, render_template, send_from_directory
from playwright.sync_api import sync_playwright
import csv, time, random, os
from datetime import datetime

app = Flask(__name__)

FORM_URL = "https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAYAAPCgaFNUM0M3Q1lMWENVQU1OU0ZQV1pFVE0xWlZOOS4u"

# Carpeta para guardar screenshots
SCREENSHOT_DIR = os.path.join("static", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def cargar_personas():
    with open("personas.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def responder_formulario(page, persona, i, numero_fijo, logs):
    page.goto(FORM_URL, wait_until="networkidle")
    page.get_by_role("textbox").first.wait_for(timeout=20000)

    textos = page.get_by_role("textbox")

    textos.nth(0).type(str(numero_fijo))
    page.get_by_role("radiogroup").nth(0).get_by_role("radio").nth(1).click()

    # Fecha
    campo_fecha = page.get_by_label("Fecha de visita")
    campo_fecha.click()
    page.wait_for_timeout(1000)

    hoy = datetime.today()
    dia_actual = hoy.day
    dia_siguiente = hoy.day+ 1
    # Seleccionar directamente el gridcell del día actual
    if page.locator(f"button[aria-label*='{dia_siguiente}']").count() > 0:
        page.locator(f"button[aria-label*='{dia_siguiente}']").first.click()
        print(f"✅ Fecha seleccionada con calendario (día {dia_siguiente})")
    else:
        # Si no existe, seleccionar el día actual
        page.locator(f"button[aria-label*='{dia_actual}']").first.click()
        print(f"✅ Fecha seleccionada con calendario (día {dia_actual})")


    # Nombre completo
    nombre = f"{persona['nombre']} {persona['apellido']}"
    textos.nth(1).type(nombre)

    # Correo dinámico
    dominio = "@gmail.com" if i % 2 == 0 else "@hotmail.com"
    correo = f"{persona['nombre'].lower()}.{persona['apellido'].lower()}{i}{dominio}"
    textos.nth(2).type(correo)

    textos.nth(3).type(persona["telefono"])

    radiogroups = page.get_by_role("radiogroup")
    calificacion = "4" if i % 2 == 0 else "5"
    radiogroups.nth(1).get_by_role("radio", name=calificacion).click()

    nps = ["8", "9", "10"][i % 3]
    radiogroups.nth(2).locator(f"label:has-text('{nps}')").click()

    if i % 3 == 0 and persona.get("comentario"):
        textos.last.type(persona["comentario"])

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

    submit_button = page.locator("button[data-automation-id='submitButton']")
    submit_button.wait_for(state="visible", timeout=30000)
    submit_button.click()

    try:
        submit_button.wait_for(state="detached", timeout=10000)
        logs.append("✅ Encuesta enviada (botón desapareció)")
    except:
        page.wait_for_selector("text=Gracias", timeout=10000)
        logs.append("✅ Encuesta enviada (mensaje de Gracias)")

    screenshot_path = os.path.join(SCREENSHOT_DIR, f"debug_envio_{i}.png")
    page.screenshot(path=screenshot_path)
    logs.append(f"📸 Screenshot guardado: {screenshot_path}")

    time.sleep(5)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numero_fijo = request.form.get("numero_fijo")
        max_respuestas = int(request.form.get("max_respuestas"))

        personas = cargar_personas()
        random.shuffle(personas)

        logs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                slow_mo=150,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120 Safari/537.36"
            )

            for i, persona in enumerate(personas[:max_respuestas]):
                page = context.new_page()
                responder_formulario(page, persona, i, numero_fijo, logs)
                page.close()

            browser.close()

        return render_template("resultados.html", logs=logs)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
