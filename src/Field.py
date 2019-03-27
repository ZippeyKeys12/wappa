from typing import Tuple


class Field:
    def __init__(self, ID: str, object_type: str, access_type: str,
                 modifiers: Tuple[str] = None, value=None):
        pass
    
    def compile(self):
        return ""
