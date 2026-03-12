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
    page.wait_for_timeout(2000)

    page.click("a div.court-card-saibro1")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    data = proxima_sexta()
    print(f"Selecionando data: {data}")
    page.click(f"button[aria-label='{data}']")
    page.wait_for_timeout(2000)

    print(f"Selecionando horário {horario}...")
    page.click(f"button[aria-label='{horario}']")
    page.wait_for_timeout(2000)

    print("Selecionando jogador adicional...")
    page.click("#multiselect")
    page.wait_for_timeout(1000)
    page.fill("input.p-multiselect-filter", "Rafaela")
    page.wait_for_timeout(1000)
    page.click("span[data-pc-section='option']:has-text('Rafaela Garcia')")
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    print("Salvando reserva...")
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

    fazer_reserva(page, "14:00")
    fazer_reserva(page, "15:00")

    print("\n🎾 Todas as reservas concluídas!")
    browser.close()