import csv

from providers.lainox import Lainox
from providers.silko import Silko

import pdfplumber
import streamlit as st


PROVIDER_MAPPING = {
    'lainox': Lainox,
    'silko': Silko,
}

st.title("Extract products from invoice")

provider = st.selectbox('Please select provider below', PROVIDER_MAPPING.keys())
document = st.file_uploader("Upload File")

if document:
    pdf_file = pdfplumber.open(document)

    provider_class = PROVIDER_MAPPING[provider]
    products = provider_class(pdf_file).extract_products()

    st.table(products)

    with open('Invoice.csv', 'w', newline='') as invoice:
        csv_file = csv.DictWriter(
            invoice,
            delimiter=',',
            fieldnames=products[0].__dict__.keys()
        )
        csv_file.writeheader()
        csv_file.writerows([product.__dict__ for product in products])

    local_file = open('Invoice.csv', 'r')
    document_name = document.name.split(".")[0]
    st.download_button(
        f'Download {provider_class.__name__} products',
        local_file,
        file_name=f'{document_name}.csv'
    )