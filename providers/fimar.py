import re

from .base_provider import BaseProvider
from models import Product


class Fimar(BaseProvider):
    START_TEXT_FOR_PRODUCTS = 'Codice / Code Descrizione / Description UM Q.ty'
    END_TEXT_FOR_PRODUCTS = 'Colli /Total Packages'

    def fetch_invoice_date_and_number(self) -> tuple:
        invoice_details = self.first_page.extract_text()
        date = re.search(r'Data / Date Pagina / Page\n\d{2}/\d{2}/\d{4}', invoice_details).group()
        invoice_nr = re.search(r'Invoice \d{1}\.\d{3}/E', invoice_details).group()
        return date.split('\n')[-1], invoice_nr.split()[-1]

    def is_product_row(
            self,
            row: str,
    ) -> bool:
        product_ids = self.fetch_product_ids()
        for product_id in product_ids:
            if product_id in row:
                return True
        return False

    def fetch_product_ids(self):
        product_ids = []
        for page in self.pdf_file.pages:
            extracted_table = page.extract_table()
            product_ids.extend(extracted_table[9][0].split('\n'))
        return product_ids

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()

        for index, product_row in enumerate(product_details):
            product = product_row[0].split()
            p = Product(
                row_nr=str(index),
                item_no=product[0],
                description=" ".join(product[1:-6]),
                qty=product[-5],
                price=product[-4],
                total_price=product[-3],
                vat_code='N/A',
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            p.description = " ".join(product_row[1:])
            all_products.append(p)
        return all_products
