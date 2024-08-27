import re

from providers.base_provider import BaseProvider
from models import Product


class Sirman(BaseProvider):
    START_TEXT_FOR_PRODUCTS = 'PO number '
    END_TEXT_FOR_PRODUCTS = "******************************************"

    @staticmethod
    def is_product_id(word: str):
        return bool(re.search(r'\d{2}', word))

    def fetch_invoice_details(self) -> tuple:
        self.first_page = self.pdf_file.pages[0]
        if "ATTENZIONE" in self.first_page.extract_text():
            self.first_page = self.pdf_file.pages[1]
        invoice_details = self.first_page.extract_table()

        date_and_invoice_nr = invoice_details[1][0]

        date = re.search(r'\d{2}\.\d{2}\.\d{4}', date_and_invoice_nr)
        invoice_nr = re.search(r'\d{8}', date_and_invoice_nr)

        try:
            return date.group(), invoice_nr.group()
        except AttributeError:
            print('Date or invoice number could not be extracted with formats XX.XX.XXX | XXX/XXXXXXXXX')

    def extract_products(self):
        all_articles = []
        for page in self.pdf_file.pages:

            extracted_text = page.extract_text()
            page_lines = extracted_text.split('\n')
            if start_index := self.fetch_index(self.START_TEXT_FOR_PRODUCTS, page_lines):
                end_index = self.fetch_index(self.END_TEXT_FOR_PRODUCTS, page_lines) or -1
                all_product_lines = page_lines[start_index+1: end_index]
                all_products_no_headers = self.remove_lines_from_top_or_bottom(all_product_lines, remove_top=False)
                products = self.szplit_products(all_products_no_headers)
                invoice_date, invoice_nr = self.fetch_invoice_details()

                for product in products:
                    prod_line = product[0].split()
                    product_data = {
                        'article_id': prod_line[0],
                        'item_no': prod_line[1],
                        'description': " ".join(product[1:]),
                        'um': prod_line[3],
                        'qty': prod_line[2],
                        'price': "".join(prod_line[4:6]),
                        'total_price': "".join(prod_line[6:8]),
                        'vat_code': prod_line[8],
                        'invoice_date': invoice_date,
                        'invoice_nr': invoice_nr,
                    }
                    p = Product(**product_data)

                    all_articles.append(p)
            else:
                continue

        return all_articles