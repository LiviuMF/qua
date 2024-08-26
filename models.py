from dataclasses import dataclass

@dataclass
class Product:
    article_id: str
    item_no: str
    description: str
    um: str
    qty: int
    price: float
    total_price: float
    vat_code: str
    invoice_date: str
    invoice_nr: str
