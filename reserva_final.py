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

def horario_disponivel(page, horario):
    btn = page.locator(f"button[aria-label='{horario}']")
    try:
        btn.wait_for(timeout=10000)
        return btn.is_enabled()
    except:
        return False

def get_ocupante(page, quadra_nome, horario):
    print(f"\nVerificando ocupante: {quadra_nome} as {horario}...")
    page.goto("https://www.maxtennispark.xyz/bookings")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    data_sexta = proxima_sexta().split(" ")[0]  # ex: "03/04/2026"
    dia, mes, ano = data_sexta.split("/")
    dia_busca = f" {dia.lstrip('0')} DE"  # ex: " 3 DE"

    day_sections = page.locator("div.day-section").all()

    for section in day_sections:
        try:
            header = section.locator("p.day-header").inner_text().strip()
            if ano in header and dia_busca in header:
                cards = section.locator("div.booking-card").all()
                for card in cards:
                    try:
                        start_time = card.locator("p.start-time").inner_text().strip()
                        court_name = card.locator("p.court-name").inner_text().strip()
                        booked_by = card.locator("p.booked-by").inner_text().strip()
                        if start_time == horario and quadra_nome.lower() in court_name.lower():
                            nome = booked_by.replace("Agendado por:", "").strip()
                            print(f"{court_name} as {horario} -> ocupado por {nome}")
                            return f"ocupado - {nome}"
                    except:
                        continue
        except:
            continue

    return "nao encontrado"

def fazer_reserva(page, quadra_css, horario):
    print(f"\n--- Iniciando reserva das {horario} na {quadra_css} ---")
    page.goto("https://www.maxtennispark.xyz/choosecourt")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    print("Selecionando quadra...")
    page.wait_for_selector(f"div.{quadra_css}", timeout=60000)
    page.click(f"div.{quadra_css}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    data = proxima_sexta()
    print(f"Selecionando data: {data}")
    page.wait_for_selector(f"button[aria-label='{data}']", timeout=60000)
    page.click(f"button[aria-label='{data}']")
    page.wait_for_timeout(3000)

    print(f"Selecionando horario {horario}...")
    if not horario_disponivel(page, horario):
        print(f"Horario {horario} indisponivel na {quadra_css}")
        return False

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

    page.screenshot(path=f"/app/screenshots/reserva_{quadra_css}_{horario.replace(':', '')}h.png")
    print(f"Reserva das {horario} na {quadra_css} confirmada!")

    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    return True

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

    # Tenta Quadra 1 primeiro
    print("\n--- Tentando Quadra 1 ---")
    ok_q1_07 = fazer_reserva(page, "court-card-saibro1", "07:00")

    if ok_q1_07:
        fazer_reserva(page, "court-card-saibro1", "08:00")
        print("\nTodas as reservas concluidas na Quadra 1!")
    else:
        # Quadra 1 indisponivel — tenta Quadra 3
        print("\n--- Quadra 1 indisponivel, tentando Quadra 3 ---")
        ok_q3_07 = fazer_reserva(page, "court-card-saibro3", "07:00")

        if ok_q3_07:
            fazer_reserva(page, "court-card-saibro3", "08:00")
            print("\nReservas concluidas na Quadra 3!")

            # Reporta quem reservou na Quadra 1
            print("\n--- Verificando quem reservou a Quadra 1 ---")
            info_q1_07 = get_ocupante(page, "Saibro 1", "07:00")
            info_q1_08 = get_ocupante(page, "Saibro 1", "08:00")
            print(f"\nQuadra 1 as 07:00 -> {info_q1_07}")
            print(f"Quadra 1 as 08:00 -> {info_q1_08}")
        else:
            # Nenhuma disponivel
            print("\n--- Nenhuma quadra disponivel ---")
            info_q1_07 = get_ocupante(page, "Saibro 1", "07:00")
            info_q1_08 = get_ocupante(page, "Saibro 1", "08:00")
            info_q3_07 = get_ocupante(page, "Saibro 3", "07:00")
            info_q3_08 = get_ocupante(page, "Saibro 3", "08:00")
            print(f"\nQuadra 1 as 07:00 -> {info_q1_07}")
            print(f"Quadra 1 as 08:00 -> {info_q1_08}")
            print(f"Quadra 3 as 07:00 -> {info_q3_07}")
            print(f"Quadra 3 as 08:00 -> {info_q3_08}")

    browser.close()