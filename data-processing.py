import pandas as pd
import fitz
import re


def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text


def process_text(text):
    lines = text.split("\n")
    print(lines)
    items = []
    for i, line in enumerate(lines):
        if "Código" in line:
            try:
                description = line.split(' (')[0]
                code = line.split('Código: ')[1].strip(')')

                # Debug prints to inspect the lines
                print(f"Processing item: {description} - Code: {code}")
                for j in range(1, 5):
                    if i + j < len(lines):
                        print(f"Line {j} after code: {lines[i + j]}")

                # Ensure there are enough lines after the current one
                if i + 3 < len(lines):
                    quantity_line = lines[i + 1]
                    unit_price_line = lines[i + 2]
                    total_price_line = lines[i + 3]

                    # Extract quantity
                    if "Qtde.:" in quantity_line:
                        match = re.search(r'Qtde.:\s*([\d,.]+)', quantity_line)
                        if match:
                            quantity_str = match.group(1).strip()
                            print('quantity_str', quantity_str)
                        else:
                            raise ValueError("Quantity line format is incorrect")
                    else:
                        raise ValueError("Quantity line format is incorrect")

                    # Extract unit price
                    if "Vl. Unit.:" in unit_price_line or "Vl. Unit.:" in quantity_line:
                        if "Vl. Unit.:" in unit_price_line:
                            unit_price_str = unit_price_line.split("Vl. Unit.:")[1].strip()
                        else:
                            unit_price_str = quantity_line.split("Vl. Unit.:")[1].strip()
                    else:
                        raise ValueError("Unit price line format is incorrect")

                    # Extract total price
                    next_line = lines[i + 4] if (i + 4 < len(lines)) else ""
                    if "Vl. Total" in total_price_line:
                        total_price_str = next_line.strip() if next_line else total_price_line.strip()
                    else:
                        total_price_str = total_price_line.strip()

                    item = {
                        'Descrição': description,
                        'Quantidade': quantity_str,
                        'Valor Unitário': unit_price_str,
                        'Valor Total': total_price_str
                    }
                    items.append(item)
                else:
                    print(f"Error processing line: {line} - not enough lines for complete item data")
            except (IndexError, ValueError) as e:
                print(f"Error processing line: {line} - {e}")
                continue
    return items


def insert_data_into_spreadsheet(items, spreadsheet_path):
    df = pd.DataFrame(items)
    df['Valor Total'] = df['Valor Total'].str.replace('.', '').str.replace(',', '.').astype(float)

    total_row = {
        'Descrição': 'Total',
        'Valor Total': df['Valor Total'].sum()
    }

    # Append the total row to the dataframe
    df = df._append(total_row, ignore_index=True)

    # Convert back to string with comma as decimal separator
    df['Valor Total'] = df['Valor Total'].apply(lambda x: f"{x:.2f}".replace('.', ','))
    df.to_csv(spreadsheet_path, index=False, sep=';', decimal=',')


def main(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    items = process_text(text)
    spreadsheet_path = "supermarket_data.csv"
    insert_data_into_spreadsheet(items, spreadsheet_path)
    print(f"Data inserted into spreadsheet: {spreadsheet_path}")


if __name__ == "__main__":
    pdf_path = 'downloaded_pdfs/Imprimir DOCUMENTO AUXILIAR DA NOTA FISCAL DE CONSUMIDOR ELETRÔNICA.pdf'
    main(pdf_path)
