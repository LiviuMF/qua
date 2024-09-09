import re

from providers.fimar import Fimar
from models import Product


class Barth(Fimar):
    START_TEXT_FOR_PRODUCTS = 'Pos Menge Art.-Nr. Beschreibung Einzelpreis Rabatt Gesamtpreis'
    END_TEXT_FOR_PRODUCTS = 'Zwischensumme'
    PRODUCT_ID_PATTERN = r'\d{1} \d{1} Stück'

    def fetch_invoice_date_and_number(self) -> tuple:
        invoice_details = self.first_page.extract_text()
        date = re.search(r'Rechnungsdatum: \d{2}\.\d{2}\.\d{4}', invoice_details).group()
        invoice_nr = re.search(r'Invoice Nr\. RE-\d{8}', invoice_details).group()
        return date.split()[-1], invoice_nr.split()[-1]

    def is_product_row(
            self,
            row: str,
    ) -> bool:
        line_items = row.split()
        first_3_words = " ".join(line_items[:3])

        is_product_id = bool(re.search(self.PRODUCT_ID_PATTERN, first_3_words))
        return is_product_id

    def fetch_product_ids(self):
        product_ids = []
        for page in self.pdf_file.pages:
            extracted_table = page.extract_table()
            product_ids.extend(extracted_table[1][4].split('\n'))
        return product_ids

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()
        for product_row in product_details:
            product = product_row[0].split()
            p = Product(
                row_nr=product[0],
                item_no=product[1],
                description=" ".join(product[4:-6]),
                qty=product[1],
                price=product[-6],
                total_price=product[-2],
                vat_code='N/A',
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            all_products.append(p)
        return all_products
