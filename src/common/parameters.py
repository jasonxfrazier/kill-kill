from databricks.sdk.runtime import dbutils
from src.common.utils import Utils
from typing import Self
from dataclasses import field


class Parameters:
    as_dict = field(default_factory=dict)
    @classmethod
    def get(cls) -> Self:
        params = dbutils.widgets.getAll().items()
        for k, v in params:
            setattr(
                cls, 
                k, 
                Utils.infer_type_from_string(v)
            )
        setattr(
            cls,
            "as_dict",
            {
                k: Utils.infer_type_from_string(v) for k, v in params
            }
        )
        return cls