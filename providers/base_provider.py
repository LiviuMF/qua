import re

import requests

from models import Product


class BaseProvider:
    START_TEXT_FOR_PRODUCTS = "Cod. Description of goods / product description price amount code"
    END_TEXT_FOR_PRODUCTS = "Payment discount:"
    PRODUCT_ID_PATTERN = r"000\d{2}"
    PRODUCT_ROW_LENGTH = 8
    EXCLUDED_LINES = (
        START_TEXT_FOR_PRODUCTS,
        END_TEXT_FOR_PRODUCTS,
        "Delivery address",
        "Delivery note",
        "____________",

        "La Vs. Ragione Sociale",
        "fattura sono quelli",
        "sede di conferimento di",
        "Vi preghiamo di comunicarce",
        "responsabilità in caso di",
        "pagamenti non effettuati alla",
        "bancari correnti per il periodo",
        "Dichiaro sotto la mia piena responsabilit",
        "vigenti disposizioni valutarie",
        "e, pertanto, nessuna altra",
        "va a favore o a carico dell",

        'Item',
        'Delivery address:',
        'Code ',
        'ATT HORECA CONSULT SRL',
        '(Mrs Andreea Mitran)',
        'str Padurii nr 1a ap 8',
        'RO-407280 Floresti - CLUJ',
        'Romania',
        'Delivery note ',
        'Order ',
        'PO number '
    )

    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.first_page = pdf_file.pages[0]

    @staticmethod
    def fetch_index(word: str, lines: list) -> int:
        for line in lines:
            if word in line:
                return lines.index(line)

    def is_product_row(
            self,
            row: str,
    ) -> bool:
        line_items = row.split()
        first_2_words = " ".join(line_items[:2])

        is_product_id = bool(re.search(self.PRODUCT_ID_PATTERN, first_2_words))
        return is_product_id and len(line_items) >= self.PRODUCT_ROW_LENGTH

    def szplit_products(
            self,
            product_lines: list
    ) -> list:
        all_products = [[]]
        for line in product_lines:
            if self.is_product_row(row=line):
                all_products.append([])
            all_products[-1].append(line)

        return all_products[1:]

    def remove_lines_from_top_or_bottom(
            self,
            pg_lines: list,
            remove_top: bool = True
    ) -> list:
        cleaned_products = []
        for pg_line in pg_lines:
            skip_by_index = 0
            for item in pg_line:
                if any((message in item for message in self.EXCLUDED_LINES)):
                    skip_by_index += 1
                    product_line = pg_line[skip_by_index:] if remove_top else pg_line[:skip_by_index * -1]
                else:
                    product_line = pg_line

            cleaned_products.append(product_line)
        return cleaned_products

    def fetch_invoice_date_and_number(self) -> tuple:
        invoice_details = self.first_page.extract_table()
        date_and_invoice_nr = invoice_details[1][0]

        date = re.search(r'\d{2}\.\d{2}\.\d{4}', date_and_invoice_nr)
        invoice_nr = re.search(r'\d+/\d{9}', date_and_invoice_nr)

        try:
            return date.group(), invoice_nr.group()
        except AttributeError:
            print('Date or invoice number could not be extracted with formats XX.XX.XXX | XXX/XXXXXXXXX')

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()

        for product in product_details:
            p = Product(
                *(product[0].split()),
                invoice_date,
                invoice_nr
            )
            p.description = f'{p.description}  {" ".join(product[1:])}'
            p.um = p.um.replace('EA', 'BUC')
            all_products.append(p)

        return all_products

    def extract_products(self):
        for page in self.pdf_file.pages:

            extracted_text = page.extract_text()
            page_lines = extracted_text.split('\n')

            if start_index := self.fetch_index(self.START_TEXT_FOR_PRODUCTS, page_lines):
                end_index = self.fetch_index(self.END_TEXT_FOR_PRODUCTS, page_lines) or -1
                all_product_lines = page_lines[start_index:end_index]
                all_products_no_headers = self.remove_lines_from_top_or_bottom(all_product_lines)
                products = self.szplit_products(all_products_no_headers)
                all_products = self.process_product_details(products)
            else:
                continue

        return all_products

    @staticmethod
    def fetch_euro_value_for_date(euro_date):
        response = requests.get(f'https://www.cursbnr.ro/arhiva-curs-bnr-{euro_date}')
        raw_value = re.search(r'Euro</td><td class="text-center">4\.\d{3,}</td>', response.text)
        if raw_value:
            cleaned_value = re.search(r'\d\.\d{3,}', raw_value.group())
            return cleaned_value.group()

