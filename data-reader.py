from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyzbar.pyzbar as pyzbar
from selenium import webdriver
from datetime import datetime
import pandas as pd
import random
import fitz
import time
import cv2
import os


def read_qr_code(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not open or find the image: {image_path}")
        return None
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        if "http" in obj.data.decode("utf-8"):
            return obj.data.decode("utf-8")
    return None


def download_pdf(url, download_folder):
    options = webdriver.ChromeOptions()
    prefs = {"savefile.default_directory": download_folder}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--kiosk-printing')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(5)

        print_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Imprimir')]")
        print_button.click()
        time.sleep(6)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_number = random.randint(1000, 9999)
        pdf_file_name = f"ticket_{timestamp}_{random_number}.pdf"
        pdf_file_path = os.path.join(download_folder, pdf_file_name)

        driver.execute_cdp_cmd("Page.printToPDF", {
            "path": pdf_file_path,
            "format": 'A4'
        })
        time.sleep(5)

        return pdf_file_path

    finally:
        driver.quit()


def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text


def process_text(text):
    lines = text.split("\n")
    items = []
    for line in lines:
        if "Código" in line:
            try:
                description = line.split(' (')[0]
                code = line.split('Código: ')[1]
                quantity = float(lines[lines.index(line) + 1].split(':')[1].strip().split()[0])
                unit_price_str = lines[lines.index(line) + 2].split(':')[1].strip().replace('.', '').replace(',', '.')
                total_price_str = lines[lines.index(line) + 3].strip().replace('.', '').replace(',', '.')

                unit_price = float(unit_price_str) if unit_price_str.replace('.', '', 1).isdigit() else 0.0
                total_price = float(total_price_str) if total_price_str.replace('.', '', 1).isdigit() else 0.0

                item = {
                    'Descrição': description,
                    'Código': code,
                    'Quantidade': quantity,
                    'Valor Unitário': unit_price,
                    'Valor Total': total_price
                }
                items.append(item)
            except (IndexError, ValueError) as e:
                print(f"Error processing line: {line} - {e}")
                continue
    return items


def insert_data_into_spreadsheet(items, spreadsheet_path):
    df = pd.DataFrame(items)
    df.to_csv(spreadsheet_path, index=False)


def main():
    qr_code_image_path = "qrcode.png"
    qr_code_url = read_qr_code(qr_code_image_path)

    download_folder = os.path.abspath('./downloaded_pdfs')

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    if qr_code_url:
        print(f"QR Code URL: {qr_code_url}")

        pdf = download_pdf(qr_code_url, download_folder)
        pdf_path = 'downloaded_pdfs/Imprimir DOCUMENTO AUXILIAR DA NOTA FISCAL DE CONSUMIDOR ELETRÔNICA.pdf'

        text = extract_text_from_pdf(pdf_path)
        print(f"Text extracted from PDF: {text[:500]}")

        items = process_text(text)
        print(f"Items extracted: {items}")

        spreadsheet_path = "supermarket_data.csv"
        insert_data_into_spreadsheet(items, spreadsheet_path)
        print(f"Data inserted into spreadsheet: {spreadsheet_path}")
    else:
        print("QR code not found.")


if __name__ == "__main__":
    main()
