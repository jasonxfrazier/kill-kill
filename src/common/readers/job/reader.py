import ast

from databricks.sdk.runtime import dbutils as dbx


class JobReader:
    """
    Reads Databricks parameters, infers types, and sets attributes dynamically.
    Initialize:
    \tjob = JobReader()
    Attributes:
    \tjob.parameters
    \tjob.{{some parameter name}}
    Methods:
    \treader.as_dict()
    """

    def __init__(self) -> None:
        job_params = dbx.widgets.getAll().items()
        for k, v in job_params:
            setattr(self, k, self._cast_types(v))
        self.parameters = {k: self._cast_types(v) for k, v in job_params}

    def as_dict(self) -> dict[str, object]:
        return self.__dict__

    def _cast_types(self, value: str) -> object:
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
        return value
