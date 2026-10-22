from databricks.sdk.runtime import dbutils
from typing import Dict
from dataclasses import dataclass
from src.common.utils import Utils


@dataclass
class Parameters:
    @classmethod
    def get(cls) -> Dict[str, str]:
        res = {}
        for k, v in dbutils.widgets.getAll().items():
            res[k] = Utils.infer_type_from_string(v)
            setattr(cls, k, v)
        return res