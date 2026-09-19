import os
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("TENNIS_EMAIL")
SENHA = os.getenv("TENNIS_SENHA")
MEU_NOME = "João Paulo"

# Fix 1: quadras e horários alvo para filtrar reservas relevantes
QUADRAS_ALVO = ["saibro 1", "saibro 3"]
HORARIOS_ALVO = ["07:00", "08:00"]


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


# Fix 1: recebe data_sexta como parâmetro (não recalcula internamente)
# Fix 1: filtra só reservas nas quadras e horários alvo
def verificar_reservas_existentes(page, data_sexta):
    print("\nVerificando reservas existentes na sexta...")
    page.goto("https://www.maxtennispark.xyz/bookings")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    data_str = data_sexta.split(" ")[0]  # ex: "04/04/2026"
    dia, mes, ano = data_str.split("/")
    dia_busca = f" {dia.lstrip('0')} DE"

    reservas = []
    day_sections = page.locator("div.day-section").all()

    for section in day_sections:
        try:
            header = section.locator("p.day-header").inner_text().strip()
            if ano in header and dia_busca in header:
                cards = section.locator("div.booking-card").all()
                for card in cards:
                    try:
                        booked_by = card.locator("p.booked-by").inner_text().strip()
                        nome = booked_by.replace("Agendado por:", "").strip()
                        if MEU_NOME.lower() in nome.lower():
                            start_time = card.locator("p.start-time").inner_text().strip()
                            court_name = card.locator("p.court-name").inner_text().strip()

                            # Fix 1: só conta se for quadra e horário relevantes
                            if (any(q in court_name.lower() for q in QUADRAS_ALVO)
                                    and start_time in HORARIOS_ALVO):
                                reservas.append({"horario": start_time, "quadra": court_name})
                                print(f"  Reserva relevante encontrada: {court_name} às {start_time}")
                            else:
                                print(f"  Reserva ignorada (fora do escopo): {court_name} às {start_time}")
                    except:
                        continue
        except:
            continue

    return reservas


# Fix 6: recebe data_sexta como parâmetro (não recalcula internamente)
def fazer_reserva(page, quadra_css, horario, data_sexta):
    print(f"\n--- Reservando {quadra_css} às {horario} ---")
    page.goto("https://www.maxtennispark.xyz/choosecourt")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    page.wait_for_selector(f"div.{quadra_css}", timeout=60000)
    page.click(f"div.{quadra_css}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # Fix 6: usa data_sexta recebida, não recalcula
    page.wait_for_selector(f"button[aria-label='{data_sexta}']", timeout=60000)
    page.click(f"button[aria-label='{data_sexta}']")
    page.wait_for_timeout(3000)

    if not horario_disponivel(page, horario):
        print(f"  Horário {horario} indisponível em {quadra_css}")
        return False

    page.click(f"button[aria-label='{horario}']")
    page.wait_for_timeout(3000)

    page.wait_for_selector("#multiselect", timeout=60000)
    page.click("#multiselect")
    page.wait_for_timeout(1000)
    page.fill("input.p-multiselect-filter", "João Paulo")
    page.wait_for_timeout(1000)
    page.wait_for_selector("span[data-pc-section='option']:has-text('João Paulo')", timeout=60000)
    page.click("span[data-pc-section='option']:has-text('João Paulo')")
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)

    page.wait_for_selector("button[aria-label='Salvar']", timeout=60000)
    page.click("button[aria-label='Salvar']")
    page.wait_for_timeout(3000)

    page.screenshot(path=f"/app/screenshots/reserva_{quadra_css}_{horario.replace(':', '')}h.png")
    print(f"  Reserva confirmada: {quadra_css} às {horario}")

    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    return True


# Fix 6: recebe data_sexta como parâmetro (não recalcula internamente)
def cancelar_reserva(page, quadra_nome, horario, data_sexta):
    print(f"\n--- Cancelando {quadra_nome} às {horario} ---")
    page.goto("https://www.maxtennispark.xyz/bookings")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # Fix 6: usa data_sexta recebida, não recalcula
    data_str = data_sexta.split(" ")[0]
    dia, mes, ano = data_str.split("/")
    dia_busca = f" {dia.lstrip('0')} DE"

    day_sections = page.locator("div.day-section").all()
    for section in day_sections:
        try:
            header = section.locator("p.day-header").inner_text().strip()
            if ano not in header or dia_busca not in header:
                continue
            cards = section.locator("div.booking-card").all()
            for card in cards:
                try:
                    start_time = card.locator("p.start-time").inner_text().strip()
                    court_name = card.locator("p.court-name").inner_text().strip()
                    booked_by = card.locator("p.booked-by").inner_text().strip()
                    nome = booked_by.replace("Agendado por:", "").strip()

                    if (start_time == horario
                            and quadra_nome.lower() in court_name.lower()
                            and MEU_NOME.lower() in nome.lower()):

                        print(f"  Card encontrado — abrindo detalhes...")
                        card.locator("i.pi-angle-right").click()
                        page.wait_for_load_state("networkidle")
                        page.wait_for_timeout(2000)

                        page.wait_for_selector("button.cancel-button", timeout=15000)
                        page.screenshot(path=f"/app/screenshots/cancelar_{quadra_nome.replace(' ', '')}_{horario.replace(':', '')}h_antes.png")
                        page.click("button.cancel-button")
                        page.wait_for_timeout(3000)
                        page.screenshot(path=f"/app/screenshots/cancelar_{quadra_nome.replace(' ', '')}_{horario.replace(':', '')}h_depois.png")
                        print(f"  Cancelamento concluído: {quadra_nome} às {horario}")
                        return True
                except:
                    continue
        except:
            continue

    print(f"  AVISO: card não encontrado para cancelar {quadra_nome} às {horario}")
    return False


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        print("Fazendo login...")
        page.goto("https://www.maxtennispark.xyz")
        page.wait_for_timeout(2000)
        page.fill("#email1", EMAIL)
        page.fill("input.p-password-input", SENHA)
        page.click("button.p-button")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        print("Login OK!")

        # Fix 6: calcula a data UMA vez aqui e passa para todas as funções
        DATA_SEXTA = proxima_sexta()
        print(f"Data alvo: {DATA_SEXTA}")

        # ── FASE 1: verifica reservas existentes ──────────────────────────
        reservas_existentes = verificar_reservas_existentes(page, DATA_SEXTA)
        if reservas_existentes:
            print("\nJá existem reservas relevantes para sexta no seu nome:")
            for r in reservas_existentes:
                print(f"  {r['quadra']} às {r['horario']}")
            print("Nada a fazer. Encerrando.")
            browser.close()
            exit(0)

        print("\nNenhuma reserva relevante encontrada. Iniciando tentativas...")

        # ── FASE 2: tentativas de reserva ─────────────────────────────────
        ok_q1_07 = fazer_reserva(page, "court-card-saibro1", "07:00", DATA_SEXTA)

        if ok_q1_07:
            ok_q1_08 = fazer_reserva(page, "court-card-saibro1", "08:00", DATA_SEXTA)

            if ok_q1_08:
                print("\nQ1 completa (07h + 08h). Nada a cancelar.")
            else:
                ok_q3_07 = fazer_reserva(page, "court-card-saibro3", "07:00", DATA_SEXTA)

                if ok_q3_07:
                    ok_q3_08 = fazer_reserva(page, "court-card-saibro3", "08:00", DATA_SEXTA)

                    if ok_q3_08:
                        print("\nQ3 completa. Cancelando Q1 07h...")
                        cancelar_reserva(page, "Saibro 1", "07:00", DATA_SEXTA)
                    else:
                        print("\nSó Q3 07h disponível. Cancelando Q1 07h e Q3 07h...")
                        cancelar_reserva(page, "Saibro 1", "07:00", DATA_SEXTA)
                        cancelar_reserva(page, "Saibro 3", "07:00", DATA_SEXTA)
                else:
                    print("\nQ3 indisponível. Cancelando Q1 07h...")
                    cancelar_reserva(page, "Saibro 1", "07:00", DATA_SEXTA)
        else:
            ok_q3_07 = fazer_reserva(page, "court-card-saibro3", "07:00", DATA_SEXTA)

            if ok_q3_07:
                ok_q3_08 = fazer_reserva(page, "court-card-saibro3", "08:00", DATA_SEXTA)

                if ok_q3_08:
                    print("\nQ3 completa (07h + 08h). Nada a cancelar.")
                else:
                    print("\nSó Q3 07h disponível. Cancelando Q3 07h...")
                    cancelar_reserva(page, "Saibro 3", "07:00", DATA_SEXTA)
            else:
                print("\nNenhuma quadra disponível.")

    except Exception as e:
        print(f"\nERRO: {e}")
        page.screenshot(path="/app/screenshots/erro.png")
        raise
    finally:
        browser.close()
