from dataclasses import dataclass

import nflreadpy
import polars as pl

from src.common.readers.yaml.reader import YAMLReader
from src.common.utils.map_type import map_type


@dataclass
class NFLReader:
    def __init__(self, config: YAMLReader) -> None:
        self.config = config

    def function(self, function_name: str, **kwargs) -> pl.DataFrame | bool:
        if not self._check_args(function_name, **kwargs):
            return False
        return self._execute_function(function_name, **kwargs)

    def _check_args(self, function_name: str, **kwargs) -> bool:
        info = self.config.as_dict.get(function_name).get("parameters").values()
        self.func_types = {x["name"]: {"type": map_type(x.get("type")), "default": x.get("default"), "min_year": x.get("min_year")} for x in info}
        self.arg_types = kwargs.items()
        for k, v in self.arg_types:
            if not self.func_types.get(k):
                return False
            if isinstance(self.func_types.get(k).get("type"), list):
                if type(v) not in self.func_types.get(k).get("type"):
                    return False
            elif type(v) is not self.func_types.get(k).get("type"):
                return False
        return True
    
    def _execute_function(self, function_name: str, **kwargs) -> pl.DataFrame:
        func = getattr(nflreadpy, function_name)
        return func(**kwargs)
    