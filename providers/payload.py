import hashlib
import requests


invoice_data = {
    "CodUnic": "32439056",
    "Hash": 'test',
    "TipFactura": "Factura",
    "Valuta": "RON",
    "Serie": 'xx',
    "Client": {
        "Denumire": "ATT HORECA CONSULT S.R.L.",
        "CodUnic": '32439056',
        "Email": "client@example.com",
        "Telefon": "0722334455",
        "Tara": "Romania",
        "Localitate": "Bucharest",
        "Adresa": "123 Street Name",
        "Tip": 'PJ'
    },
    "Continut": [
        {
            "Denumire": "Product Name",
            "CodArticol": "PRD001",
            "PretUnitar": 100.00,
            "PretTotal": 200.00,
            "NrProduse": 2.0,
            "CotaTVA": "19.0",
            "UM": "BUC",
            "Descriere": "This is a detailed description of the product"
        }
    ],
    "PlatformaURL": 'https://qua-providers.streamlit.app'
}

company_unique_code = "32439056"
private_key = "A2235B87937F185C355EFEB0CABB0538"
client_name = 'ATT HORECA CONSULT S.R.L.'
hash_string = f"{company_unique_code}{private_key}{client_name}"
hash_value = hashlib.sha1(hash_string.encode('utf-8')).hexdigest().upper()
invoice_data['Hash'] = hash_value

def create_invoice(invoice_data):
    return requests.post('https://api.fgo.ro/v1/factura/emitere', json=invoice_data)
