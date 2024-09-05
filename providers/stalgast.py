import re

from .base_provider import BaseProvider
from models import Product


class Stalgast(BaseProvider):
    START_TEXT_FOR_PRODUCTS = 'number % value amount amount'
    END_TEXT_FOR_PRODUCTS = 'Net amount.....'
    PRODUCT_ID_PATTERN = r'\d{1} [A-Z]{1}'
    PRODUCT_ROW_LENGTH = 12

    def fetch_invoice_date_and_number(self) -> tuple:
        extracted_text = self.first_page.extract_text()
        date = re.search(r"Document date: \d{1,2}/\d{2}/\d{4}", extracted_text)
        invoice_nr = re.search(r"Number: [A-Z]{2}\d{8}", extracted_text)
        try:
            cleaned_date = date.group().replace('Document date: ', '')
            cleaned_number = invoice_nr.group().replace('Number: ', '')
            return cleaned_date, cleaned_number
        except AttributeError:
            print('Date or invoice number could not be extracted with formats XX/XX/XXX | FS/XXXXXXXX')

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()
        for product_row in product_details:
            product = product_row[0].split()
            p = Product(
                row_nr=product[0],
                item_no=product[1],
                description=" ".join(product[2:-9]),
                qty=product[-9],
                price=product[-7],
                total_price=product[-1],
                vat_code='N/A',
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            p.description = f'{p.description}  {" ".join(product_row[1:])}'
            all_products.append(p)

        return all_products
