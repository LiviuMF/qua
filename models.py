from dataclasses import dataclass

@dataclass
class Product:
    row_nr: str
    item_no: str
    description: str
    qty: str
    price: str
    total_price: str
    vat_code: str
    invoice_date: str
    invoice_nr: str
    um: str = 'BUC'
