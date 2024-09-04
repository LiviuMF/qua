from dataclasses import dataclass

@dataclass
class Product:
    row_nr: str
    item_no: str
    description: str
    um: str
    qty: str
    price: str
    total_price: str
    vat_code: str
    invoice_date: str
    invoice_nr: str
