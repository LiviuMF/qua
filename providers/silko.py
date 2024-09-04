from .base_provider import BaseProvider


class Silko(BaseProvider):
    def __init__(self, pdf_file):
        super().__init__(pdf_file=pdf_file)
