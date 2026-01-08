from playwright.sync_api import sync_playwright
import csv
import time
import random
from datetime import datetime

FORM_URL = "https://forms.cloud.microsoft/r/0zYh9nCSX9"

def cargar_personas():
    with open("personas.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def responder_formulario(page, persona, i, numero_fijo):
    page.goto(FORM_URL, wait_until="networkidle")
    page.get_by_role("textbox").first.wait_for(timeout=20000)

    textos = page.get_by_role("textbox")

    textos.nth(0).fill(numero_fijo)

    page.get_by_role("radiogroup").nth(0).get_by_role("radio").nth(1).click()

    page.locator(
        'input[placeholder="Especifique la fecha (d/M/yyyy)"]'
    ).fill(datetime.today().strftime("%d/%m/%Y"))

    textos.nth(1).fill(f"{persona['nombre']} {persona['apellido']}")

    dominio = "@gmail.com" if i % 2 == 0 else "@hotmail.com"
    correo = f"{persona['nombre'].lower()}{i}{dominio}"
    textos.nth(2).fill(correo)

    textos.nth(3).fill(persona["telefono"])

    page.get_by_role("button", name="Enviar").click()
    time.sleep(5)

def ejecutar_bot(max_respuestas, numero_fijo):
    personas = cargar_personas()
    random.shuffle(personas)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        for i, persona in enumerate(personas[:max_respuestas]):
            page = context.new_page()
            responder_formulario(page, persona, i, numero_fijo)
            page.close()

        browser.close()
