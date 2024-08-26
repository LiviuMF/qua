import re

from models import Product


START_TEXT_FOR_PRODUCTS = "Cod. Description of goods / product description price amount code"
END_TEXT_FOR_PRODUCTS = "Payment discount:"


class Lainox:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.first_page = pdf_file.pages[0]

    @staticmethod
    def fetch_index(word: str, lines: list) -> int:
        for line in lines:
            if word in line:
                return lines.index(line)

    @staticmethod
    def is_product_id(word: str):
        return bool(re.search(r'000\d{2}0', word))

    def szplit_products(self, product_lines: list) -> list:
        all_products = []
        for line in product_lines:
            if self.is_product_id(line.split()[0]):
                all_products.append([])
            all_products[-1].append(line)

        return all_products

    @staticmethod
    def remove_product_header(pg_lines: list) -> list:
        skip_by_index = 0
        for pg_line in pg_lines:
            if any((message in pg_line for message in (
                    START_TEXT_FOR_PRODUCTS,
                    "Delivery address",
                    "Delivery note",
                    "____________"
            ))):
                skip_by_index += 1
        return pg_lines[skip_by_index:]

    def fetch_invoice_details(self) -> tuple:
        invoice_details = self.first_page.extract_table()
        date_and_invoice_nr = invoice_details[1][0]

        date = re.search(r'\d{2}\.\d{2}\.\d{4}', date_and_invoice_nr)
        invoice_nr = re.search(r'\d+/\d{9}', date_and_invoice_nr)

        try:
            return date.group(), invoice_nr.group()
        except AttributeError:
            print('Date or invoice number could not be extracted with formats XX.XX.XXX | XXX/XXXXXXXXX')

    def extract_products(self):
        all_articles = []
        for page in self.pdf_file.pages:

            extracted_text = page.extract_text()
            page_lines = extracted_text.split('\n')

            if start_index := self.fetch_index(START_TEXT_FOR_PRODUCTS, page_lines):
                end_index = self.fetch_index(END_TEXT_FOR_PRODUCTS, page_lines) or -1
                all_product_lines = page_lines[start_index:end_index]
            else:
                continue

            all_products_no_headers = self.remove_product_header(all_product_lines)
            products = self.szplit_products(all_products_no_headers)
            invoice_date, invoice_nr = self.fetch_invoice_details()

            for product in products:
                p = Product(
                    *(product[0].split()),
                    invoice_date,
                    invoice_nr
                )
                p.description = p.description + " ".join(product[1:])
                p.um = p.um.replace('EA', 'BUC')
                all_articles.append(p)
        return all_articles
