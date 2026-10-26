import argparse
import ast
import sys


class JobReader:
    """
    Reads command-line arguments, infers types, and sets attributes dynamically.
    Initialize:
    \tjob = JobReader()
    Attributes:
    \tjob.parameters
    \tjob.<parameter_name>
    Methods:
    \tjob.as_dict()
    """

    def __init__(self) -> None:
        parser = argparse.ArgumentParser()
        for arg in sys.argv[1:]:
            if arg.startswith("--"):
                parser.add_argument(arg.split("=")[0])
        args = parser.parse_args()
        self.parameters = {
            k: self._cast_types(v)
            for k, v in vars(args).items()
            if v is not None
        }
        for k, v in self.parameters.items():
            setattr(self, k, v)

    def as_dict(self) -> dict[str, object]:
        return self.parameters.copy()

    @staticmethod
    def _cast_types(value: str) -> object:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        if value.lower() in ("null", "none"):
            return None

        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value