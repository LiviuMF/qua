import re

import dateutil

from .base_provider import BaseProvider
from models import Product


class Sayl(BaseProvider):
    START_TEXT_FOR_PRODUCTS = 'Albarán Ref Cliente Artículo Denominación Cantidad Precio DTO (%) Total'
    END_TEXT_FOR_PRODUCTS = 'Total bruto Total dto. Base'
    PRODUCT_ID_PATTERN = r'AC\d{4}'

    def is_product_row(
            self,
            row: str,
    ) -> bool:
        line_items = row.split()
        first_2_words = " ".join(line_items[:2])

        is_product_id = bool(re.search(self.PRODUCT_ID_PATTERN, first_2_words))
        return is_product_id

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()

        for index, product_row in enumerate(product_details):
            product = product_row[0].split()
            p = Product(
                row_nr=str(index),
                item_no=product[0],
                description=" ".join(product[2:-5]),
                qty=product[-5],
                price=product[-4],
                total_price=product[-1],
                vat_code='N/A',
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            all_products.append(p)
        return all_products

    def fetch_invoice_date_and_number(self) -> tuple:
        invoice_details = self.first_page.extract_text()
        date_and_invoice = re.search(r'Factura: Fecha: Cod. Cliente\nF - \d{4} \d{2}/\d{2}/\d{4}', invoice_details).group()
        date = date_and_invoice.split()[-1]
        invoice_nr = re.search(r'F - \d{4}', date_and_invoice).group()

        return date, invoice_nr
