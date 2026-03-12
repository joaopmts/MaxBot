import os
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("TENNIS_EMAIL")
SENHA = os.getenv("TENNIS_SENHA")

def proxima_sexta():
    hoje = datetime.today()
    dias_ate_sexta = (4 - hoje.weekday()) % 7
    if dias_ate_sexta == 0:
        dias_ate_sexta = 7
    sexta = hoje + timedelta(days=dias_ate_sexta)
    return sexta.strftime("%d/%m/%Y Sexta-Feira")

def fazer_reserva(page, horario):
    print(f"\n--- Iniciando reserva das {horario} ---")

    page.goto("https://www.maxtennispark.xyz/choosecourt")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    print("Selecionando quadra...")
    page.wait_for_selector("a div.court-card-saibro1", timeout=60000)
    page.click("a div.court-card-saibro1")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    data = proxima_sexta()
    print(f"Selecionando data: {data}")
    page.wait_for_selector(f"button[aria-label='{data}']", timeout=60000)
    page.click(f"button[aria-label='{data}']")
    page.wait_for_timeout(3000)

    print(f"Selecionando horário {horario}...")
    page.wait_for_selector(f"button[aria-label='{horario}']", timeout=60000)
    page.click(f"button[aria-label='{horario}']")
    page.wait_for_timeout(3000)

    print("Selecionando jogador adicional...")
    page.wait_for_selector("#multiselect", timeout=60000)
    page.click("#multiselect")
    page.wait_for_timeout(1000)
    page.fill("input.p-multiselect-filter", "Rafaela")
    page.wait_for_timeout(1000)
    page.wait_for_selector("span[data-pc-section='option']:has-text('Rafaela Garcia')", timeout=60000)
    page.click("span[data-pc-section='option']:has-text('Rafaela Garcia')")
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    print("Salvando reserva...")
    page.wait_for_selector("button[aria-label='Salvar']", timeout=60000)
    page.click("button[aria-label='Salvar']")
    page.wait_for_timeout(3000)

    page.screenshot(path=f"/app/screenshots/reserva_{horario.replace(':', '')}h.png")
    print(f"✅ Reserva das {horario} confirmada!")

    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Fazendo login...")
    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_timeout(2000)
    page.fill("#email1", EMAIL)
    page.fill("input.p-password-input", SENHA)
    page.click("button.p-button")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    print("Login OK!")

    fazer_reserva(page, "07:00")
    fazer_reserva(page, "08:00")

    print("\n🎾 Todas as reservas concluídas!")
    browser.close()