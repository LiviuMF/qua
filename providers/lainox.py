from .base_provider import BaseProvider


class Lainox(BaseProvider):
    def __init__(self, pdf_file):
        super().__init__(pdf_file)

    def szplit_products(self, product_lines: list) -> list:
        all_products = []
        for line in product_lines:
            if self.is_product_id(line.split()[0]):
                all_products.append([])
            all_products[-1].append(line)

        return all_products
