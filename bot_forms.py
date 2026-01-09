from playwright.sync_api import sync_playwright
import csv
import time
import random
from datetime import datetime



FORM_URL = "https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAYAAPCgaFNUM0M3Q1lMWENVQU1OU0ZQV1pFVE0xWlZOOS4u"

def cargar_personas():
    with open("personas.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def responder_formulario(page, persona, i, numero_fijo):
    page.goto(FORM_URL, wait_until="networkidle")
    page.get_by_role("textbox").first.wait_for(timeout=20000)

    textos = page.get_by_role("textbox")

    # 🔹 Número fijo dinámico
    textos.nth(0).fill(numero_fijo)

    page.get_by_role("radiogroup").nth(0).get_by_role("radio").nth(1).click()

    
    hoy = datetime.today()
    fecha_texto = f"{hoy.day}/{hoy.month:02d}/{hoy.year}"

    campo_fecha = page.get_by_label("Fecha de visita")

    campo_fecha.click()
    campo_fecha.press("Control+A")
    campo_fecha.type(fecha_texto, delay=120)

    nombre_completo = f"{persona['nombre']} {persona['apellido']}"
    textos.nth(1).fill(nombre_completo)

    dominio = "@gmail.com" if i % 2 == 0 else "@hotmail.com"
    nombre = persona["nombre"].lower()
    apellido = persona["apellido"].lower()

    patrones = [
        f"{nombre}.{apellido}",
        f"{nombre}{apellido[0]}",
        f"{nombre[0]}_{apellido}",
        f"{apellido}.{nombre}",
        f"{nombre}{apellido}{i % 100}"
    ]

    correo = f"{patrones[i % len(patrones)]}{dominio}"
    textos.nth(2).fill(correo)

    textos.nth(3).fill(persona["telefono"])

    radiogroups = page.get_by_role("radiogroup")
    calificacion = "4" if i % 2 == 0 else "5"
    radiogroups.nth(1).get_by_role("radio", name=calificacion).click()

    nps = ["8", "9", "10"][i % 3]
    radiogroups.nth(2).locator(f"label:has-text('{nps}')").click()

    if i % 3 == 0 and persona.get("comentario"):
        textos.last.fill(persona["comentario"])

    boton_enviar = page.locator('[data-automation-id="submitButton"]')
    boton_enviar.scroll_into_view_if_needed()
    boton_enviar.click()

    time.sleep(5)


def ejecutar_bot(max_respuestas=6, numero_fijo="101"):
    personas = cargar_personas()
    random.shuffle(personas)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=150)
        context = browser.new_context()

        for i, persona in enumerate(personas[:max_respuestas]):
            page = context.new_page()
            try:
                responder_formulario(page, persona, i, numero_fijo)
                time.sleep(random.uniform(12, 20))
            except Exception as e:
                print("❌ Error:", e)
            finally:
                page.close()

        browser.close()

    # ✅ SOLO CUANDO TERMINA TODO
    with open("estado.txt", "w", encoding="utf-8") as f:
        f.write("FINALIZADO")
