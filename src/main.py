from dataclasses import dataclass

import nflreadpy
import polars as pl

from common import YAMLReader, map_type


@dataclass
class NFLReader:
    def __init__(self, config: YAMLReader) -> None:
        self.config = config

    def function(self, function_name: str, **kwargs) -> pl.DataFrame | None:
        if not self._check_args(function_name, **kwargs):
            return False
        return self._execute_function(function_name, **kwargs)

    def _check_args(self, function_name: str, **kwargs) -> bool:
        info = self.config.as_dict.get(function_name).get("parameters").values()
        func_types = {x["name"]: map_type(x["type"]) for x in info}
        arg_types = kwargs.items()
        for k, v in arg_types:
            if not func_types.get(k):
                return False
            if isinstance(func_types.get(k), list):
                if type(v) not in func_types.get(k):
                    return False
            elif type(v) is not func_types.get(k):
                return False
        return True

    def _execute_function(self, function_name: str, **kwargs) -> pl.DataFrame:
        func = getattr(nflreadpy, function_name)
        return func(**kwargs)


if __name__ == "__main__":
    nfl = NFLReader(YAMLReader("functions.yml"))
    df = nfl.function("load_player_stats")
