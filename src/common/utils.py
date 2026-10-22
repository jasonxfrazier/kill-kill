import ast
from typing import Type

class Utils:
    @staticmethod
    @classmethod
    def infer_type_from_string(value: str) -> Type | str:
        try:
            parsed_val = ast.literal_eval(value)
            return type(parsed_val)
        except (ValueError, SyntaxError):
            return str