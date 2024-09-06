import re

from .base_provider import BaseProvider
from models import Product


class GastroMetal(BaseProvider):
    PRODUCT_ID_PATTERN = r'\d{1}'
    PRODUCT_ROW_LENGTH = 9

    def extract_products(self):
        all_products = []
        for page in self.pdf_file.pages:

            extracted_table = page.extract_table()
            product_details = [
                row for row in extracted_table[2:]
                if self.is_product_row(row)
            ]
            all_products.extend(product_details)

        clean_products = self.process_product_details(all_products)

        return clean_products

    def is_product_row(
            self,
            row: str,
    ) -> bool:
        is_product_id = bool(re.search(self.PRODUCT_ID_PATTERN, str(row[0])))
        return is_product_id and len(row) >= self.PRODUCT_ROW_LENGTH

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()

        for product in product_details:
            p = Product(
                row_nr=product[0],
                item_no=product[0],
                description=product[1],
                qty=product[5].split()[1],
                price=product[6],
                total_price=product[7],
                vat_code=product[8],
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            all_products.append(p)
        return all_products

    def fetch_invoice_date_and_number(self) -> tuple:
        invoice_details = self.first_page.extract_text()
        date = re.search(r'Data: \d{2}\.\d{2}\.\d{4}', invoice_details).group()
        invoice_nr = re.search(r'Numar factura: GMT\d{6}', invoice_details).group()
        return date.split()[-1], invoice_nr.split()[-1]
