from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Abre o browser visível (headless=False)
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Abrindo o site...")
    page.goto("https://www.maxtennispark.xyz")

    # Espera 2 segundos para carregar
    page.wait_for_timeout(2000)

    # Tira um screenshot
    page.screenshot(path="screenshot.png")
    print("Screenshot salvo!")

    # Mantém o browser aberto por 5 segundos para você ver
    page.wait_for_timeout(5000)
    browser.close()