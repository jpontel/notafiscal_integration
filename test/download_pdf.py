from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os


def download_pdf_from_url(url, download_folder):
    options = webdriver.ChromeOptions()
    prefs = {"savefile.default_directory": download_folder}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--kiosk-printing')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        # Aguardar até que a página carregue completamente
        time.sleep(5)  # Ajuste o tempo conforme necessário

        # Procurar e clicar no link "Imprimir"
        print_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Imprimir')]")
        print_button.click()

        # Aguardar a janela de impressão abrir
        time.sleep(6)  # Ajuste o tempo conforme necessário

        # Definir o caminho do arquivo para salvar o PDF
        pdf_file_path = os.path.join(download_folder, "nota_fiscal.pdf")

        # Usar o comando Chrome DevTools Protocol (CDP) para salvar como PDF
        driver.execute_cdp_cmd("Page.printToPDF", {
            "path": pdf_file_path,
            "format": 'A4'
        })
        time.sleep(5)  # Ajuste o tempo conforme necessário para o download ser concluído

    finally:
        driver.quit()


def main():
    url = 'http://www.fazenda.pr.gov.br/nfce/qrcode?p=41240693209765014177652050000581521426210597%7C2%7C1%7C1%7CAC44DCD20169E50D0AF9ABF2581000B4C95842EF'

    # Pasta onde o PDF será salvo
    download_folder = os.path.abspath('./downloaded_pdfs')

    # Certificar-se de que a pasta de download existe
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Chamar a função para baixar o PDF
    download_pdf_from_url(url, download_folder)


if __name__ == '__main__':
    main()
