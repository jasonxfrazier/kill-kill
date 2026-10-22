from databricks.sdk.runtime import dbutils
from typing import Dict
from dataclasses import dataclass


@dataclass
class Parameters:
    @classmethod
    def get(cls) -> Dict[str, str]:
        res = {}
        for k, v in dbutils.widgets.getAll().items():
            res[k] = v
            setattr(cls, k, v)
        return res