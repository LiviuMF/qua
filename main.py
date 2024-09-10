import csv
from datetime import datetime
import traceback

from providers.ali_parts import AliParts
from providers.barth import Barth
from providers.base_provider import BaseProvider
from providers.fimar import Fimar
from providers.gastrometal import GastroMetal
from providers.lainox import Lainox
from providers.oem import Oem
from providers.sayl import Sayl
from providers.silko import Silko
from providers.sirman import Sirman
from providers.stalgast import Stalgast
from providers.virtus import Virtus

import pdfplumber
import streamlit as st


PROVIDER_MAPPING = {
    'ali_parts': AliParts,
    'barth': Barth,
    'fimar': Fimar,
    'gastrometal': GastroMetal,
    'lainox': Lainox,
    'oem': Oem,
    'sayl': Sayl,
    'silko': Silko,
    'sirman': Sirman,
    'stalgast': Stalgast,
    'virtus': Virtus,
}


st.set_page_config(page_title='Invoice product extractor', page_icon='favicon.ico')
st.title("Extract products from invoice")

provider = st.selectbox('Please select provider below', PROVIDER_MAPPING.keys())
document = st.file_uploader("Upload File")

if st.button("Create invoice"):
    response = BaseProvider.create_invoice()
    st.success(f"invoice created with response: {response.content}")

def run():
    provider_class = PROVIDER_MAPPING[provider]

    if document:
        pdf_file = pdfplumber.open(document)

        products = provider_class(pdf_file).extract_products()

        if len(products) > 1 and provider == 'virtus':
            st.warning(
                'Provider Virtus is still WIP, for multiple invoice entries,please make sure data is extracted correctly'
            )
        elif len(products) == 0:
            st.error(
                f'Please make sure {document.name} is for {provider} provider'
            )

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


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        BaseProvider.notify_telegram(
            f'Qua providers failed with the following exception: {e}'
            f'\nFile uploaded: {document.name} for provider: {provider}'
            f'\nTraceback: {traceback.format_exc()}'
        )
        st.exception(e)
