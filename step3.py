from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

EMAIL = "joao.paulo@maxtennispark.xyz"
SENHA = "Mudar@123"

def proxima_sexta():
    hoje = datetime.today()
    dias_ate_sexta = (4 - hoje.weekday()) % 7
    if dias_ate_sexta == 0:
        dias_ate_sexta = 7
    sexta = hoje + timedelta(days=dias_ate_sexta)
    return sexta.strftime("%d/%m/%Y Sexta-Feira")

def fazer_reserva(page, horario):
    print(f"\n--- Iniciando reserva das {horario} ---")

    # ── Ir para escolha de quadra ──────────────────
    print("Navegando para agendamento...")
    page.goto("https://www.maxtennispark.xyz/choosecourt")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # ── Clicar na quadra ───────────────────────────
    print("Selecionando quadra...")
    page.click("a div.court-card-saibro1")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # ── Clicar na próxima sexta-feira ──────────────
    data = proxima_sexta()
    print(f"Selecionando data: {data}")
    page.click(f"button[aria-label='{data}']")
    page.wait_for_timeout(2000)

    # ── Clicar no horário ─────────────────────────
    print(f"Selecionando horário {horario}...")
    page.click(f"button[aria-label='{horario}']")
    page.wait_for_timeout(2000)

    # ── Selecionar jogador no multiselect ──────────
    print("Selecionando jogador adicional...")
    page.click("#multiselect")
    page.wait_for_timeout(1000)
    page.fill("input.p-multiselect-filter", "Rafaela")
    page.wait_for_timeout(1000)
    page.click("span[data-pc-section='option']:has-text('Rafaela Garcia')")
    page.wait_for_timeout(500)
    page.keyboard.press("Escape")
    page.wait_for_timeout(1000)
    print("Jogador selecionado!")

    # ── Salvar reserva ─────────────────────────────
    print("Salvando reserva...")
    page.click("button[aria-label='Salvar']")
    page.wait_for_timeout(3000)

    page.screenshot(path=f"reserva_{horario.replace(':', '')}h.png")
    print(f"✅ Reserva das {horario} confirmada!")

    # ── Voltar para a home ─────────────────────────
    print("Voltando para a home...")
    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # ── Login (apenas uma vez) ─────────────────────
    print("Abrindo o site...")
    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_timeout(2000)

    print("Fazendo login...")
    page.fill("#email1", EMAIL)
    page.fill("input.p-password-input", SENHA)
    page.click("button.p-button")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    print("Login OK!")

    # ── Duas reservas ──────────────────────────────
    fazer_reserva(page, "07:00")
    fazer_reserva(page, "08:00")

    print("\n🎾 Todas as reservas concluídas!")
    page.wait_for_timeout(5000)
    browser.close()