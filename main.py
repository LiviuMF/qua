import csv
from datetime import datetime

from providers.lainox import Lainox
from providers.silko import Silko
from providers.sirman import Sirman

import pdfplumber
import streamlit as st


PROVIDER_MAPPING = {
    'lainox': Lainox,
    'silko': Silko,
    'sirman': Sirman,
}

st.set_page_config(page_title='Invoice product extractor', page_icon='favicon.ico')
st.title("Extract products from invoice")

provider = st.selectbox('Please select provider below', PROVIDER_MAPPING.keys())
document = st.file_uploader("Upload File")

provider_class = PROVIDER_MAPPING[provider]

if document:
    pdf_file = pdfplumber.open(document)

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

euro_date = st.date_input('Please select date for euro rate', max_value=datetime.now().date())
if st.button('Get rate'):
    euro_value = provider_class.fetch_euro_value_for_date(euro_date.isoformat())
    st.success(euro_value)