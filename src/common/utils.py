import ast
from typing import Any


class Utils:
    @staticmethod
    def infer_type_from_string(value: str) -> Any:
        if value == "true":
            return True
        if value == "false":
            return False
        if value in ["null", "Null", "none"]:
            return None
        try:
            val = ast.literal_eval(value)
            if isinstance(val, list):
                return [
                    Utils.infer_type_from_string(v) if isinstance(v, str) else v for v in val
                ]
            if isinstance(val, dict):
                return {
                    k: Utils.infer_type_from_string(v) if isinstance(v, str) else v
                    for k, v in val.items()
                }
            return val
        except (ValueError, SyntaxError, TypeError):
            return value