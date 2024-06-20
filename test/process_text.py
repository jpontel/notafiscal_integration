import fitz


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
                unit_price_str = lines[lines.index(line) + 2].split(':')[1].strip()
                total_price_str = lines[lines.index(line) + 3].strip()
                print(description, unit_price_str, total_price_str)

                unit_price = float(unit_price_str.replace(',', '.')) if unit_price_str.replace(',', '.').replace('.',
                                                                                                                 '').isdigit() else 0.0
                total_price = float(total_price_str.replace(',', '.')) if total_price_str.replace(',', '.').replace('.',
                                                                                                                    '').isdigit() else 0.0

                item = {
                    'description': description,
                    'code': code,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price
                }
                items.append(item)
            except (IndexError, ValueError) as e:
                print(f"Error processing line: {line} - {e}")
                continue
    return items


def main():
    pdf_path = "./../downloaded_pdfs/Imprimir DOCUMENTO AUXILIAR DA NOTA FISCAL DE CONSUMIDOR ELETRÔNICA.pdf"
    text = extract_text_from_pdf(pdf_path)
    print(f"Text extracted from PDF: {text[:500]}")

    items = process_text(text)
    print(f"Items extracted: {items}")

