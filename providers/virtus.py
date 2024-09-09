import re

from .base_provider import BaseProvider
from models import Product


class Virtus(BaseProvider):
    PRODUCT_ID_PATTERN = r'\d{4} .* PZ \d{1,5}\.\d{2} \d{1,5}\.\d{2} \d{1,2}\.\d{2} \d{1,5}.\d{2}'
    END_TEXT_FOR_PRODUCTS = '%VAT VAT VAT EXCEMPTION VALUES OF GOODS (NOT TAXABLE)'

    def fetch_invoice_date_and_number(self) -> tuple:
        invoice_details = self.first_page.extract_text()
        date_and_invoice_nr = re.search(
            r'\d{2}/\d{2}/\d{4} \d{4}-\d{4}',
            invoice_details).group()
        date, invoice_nr = date_and_invoice_nr.split()
        return date, invoice_nr

    def is_product_row(
            self,
            row: str,
    ) -> bool:
        if re.search(self.PRODUCT_ID_PATTERN, row):
            return True
        return False

    def extract_products(self):
        all_products = []
        for page in self.pdf_file.pages:
            extracted_text = page.extract_text()
            page_lines = extracted_text.split('\n')
            products = [
                product_row
                for product_row in page_lines
                if self.is_product_row(product_row)
            ]
            all_products.extend(self.process_product_details(products))
        return all_products

    def process_product_details(self, product_details: list):
        all_products = []
        INTRA_STAT = re.search(r'INTRA-STAT : \d{8}', self.first_page.extract_text()).group()
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()
        for index, product_row in enumerate(product_details):
            product = product_row.split()
            p = Product(
                row_nr=str(index+1),
                item_no=product[0],
                description=f'{" ".join(product[1:-6])}\n{INTRA_STAT}',
                qty=product[-4],
                price=product[-3],
                total_price=product[-1],
                vat_code='N/A',
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            all_products.append(p)

        return all_products
