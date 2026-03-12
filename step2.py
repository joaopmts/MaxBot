from playwright.sync_api import sync_playwright

EMAIL = "joao.paulo@maxtennispark.xyz"  # <- coloque seu email aqui
SENHA = "Mudar@123"      # <- coloque sua senha aqui

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Abrindo o site...")
    page.goto("https://www.maxtennispark.xyz")
    page.wait_for_timeout(2000)

    print("Preenchendo email...")
    page.fill("#email1", EMAIL)

    print("Preenchendo senha...")
    page.fill("input.p-password-input", SENHA)

    print("Clicando em Login...")
    page.click("button.p-button")

    # Aguarda a próxima página carregar
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    page.screenshot(path="pos_login.png")
    print("Login feito! Screenshot salvo em pos_login.png")

    page.wait_for_timeout(5000)
    browser.close()