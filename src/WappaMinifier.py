import re


class WappaMinifier:
    WS = re.compile(r"\s+", flags=re.IGNORECASE)

    def __init__(self):
        pass

    def zscript(self, text: str) -> str:
        return text
