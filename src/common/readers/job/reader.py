from databricks.sdk.runtime import dbutils as dbx
import ast

class JobReader:
    def __init__(self) -> None:
        job_params = dbx.widgets.getAll().items()
        for k, v in job_params:
            setattr(self, k, self._cast_types(v))
        self.parameters = {
            k: self._cast_types(v)
            for k, v in job_params
        }

    def as_dict(self) -> dict[str, object]:
        return self.__dict__
    
    def _cast_types(self, value: str) -> object:
        """
        Will infer a strings type and try to replace it with its type correct form.
        """
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
