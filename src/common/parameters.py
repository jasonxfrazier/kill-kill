from databricks.sdk.runtime import dbutils
from src.common.utils import Utils # ty: ignore[unresolved-import]
from typing import Self
from dataclasses import field


class Parameters:
    """
    Contains Environment Varables.
    Usage:
        parameters = Parameters.get()
        parameters.expected_parameter
        parameters.as_dict
    """
    as_dict = field(default_factory=dict)
    @classmethod
    def get(cls) -> Self:
        params = dbutils.widgets.getAll().items() # ty: ignore[unresolved-attribute]
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
        return cls # ty: ignore[invalid-return-type]