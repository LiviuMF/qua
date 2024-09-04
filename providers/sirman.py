import re

from providers.base_provider import BaseProvider
from models import Product


class Sirman(BaseProvider):
    START_TEXT_FOR_PRODUCTS = 'Material/Description Quantity Price Value VAT'
    END_TEXT_FOR_PRODUCTS = "******************************************"
    PRODUCT_ID_PATTERN = r"\d{2,3} {1}"
    PRODUCT_ROW_LENGTH = 9

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
                all_product_lines = page_lines[start_index:end_index]
                products = self.szplit_products(all_product_lines)
                clean_products = self.remove_lines_from_top_or_bottom(products, remove_top=False)

                invoice_date, invoice_nr = self.fetch_invoice_details()

                for product_row in clean_products:
                    product = product_row[0].split()
                    p = Product(
                        row_nr=product[0],
                        item_no=product[1],
                        description="",
                        um=product[3],
                        qty=product[2],
                        price="".join(product[4:6]),
                        total_price=product[6],
                        vat_code=product[-1],
                        invoice_date=invoice_date,
                        invoice_nr=invoice_nr,
                    )
                    p.description = p.description + " ".join(product_row[1:])
                    p.um = p.um.replace('PC', 'BUC')
                    all_articles.append(p)
            else:
                continue

        return all_articles
