from .base_provider import BaseProvider
from models import Product


class Oem(BaseProvider):
    START_TEXT_FOR_PRODUCTS = '_ _ _ _ _ _ _ _ _C_o_d_._____ _ _ _ P_r_o_d_u_c_t_ d__e_s_c_ri_p_ti_o_n'
    END_TEXT_FOR_PRODUCTS = 'Summary Custom code Quantity Net weight Kg Gross weight Kg Total'

    def process_product_details(self, product_details: list):
        all_products = []
        invoice_date, invoice_nr = self.fetch_invoice_date_and_number()
        for product_row in product_details:
            product = product_row[0].split()
            p = Product(
                row_nr=product[0],
                item_no=product[1],
                description=product[2],
                qty=product[4],
                price=product[5],
                total_price=product[8],
                vat_code=product[-1],
                invoice_date=invoice_date,
                invoice_nr=invoice_nr,
            )
            p.description = f'{p.description}  {" ".join(product_row[1:])}'
            all_products.append(p)

        return all_products