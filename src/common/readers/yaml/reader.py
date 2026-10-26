from dataclasses import dataclass
from pathlib import Path

import yaml

from src.common.utils.map_type import map_type


@dataclass
class Parameter:
    name: str
    description: str
    types: type | list[type]
    default: str | bool | None
    min_year: int | None
    options: list[str] | None


@dataclass
class Function:
    name: str
    description: str
    returns: type
    parameters: list[Parameter]


class YAMLReader:
    """
    Parses YAML file containing informationa about `nflreadpy` function api info.
    Initialize:
    \treader = YAMLReader('path/to/file.yaml')
    Attributes:
    \treader.path
    \treader.as_dict
    Methods:
    \treader.get.functions()
    \treader.get.function_names()
    \treader.get.function_info()
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._functions: list[Function] = []
        self.as_dict: dict[str, object] = {}
        self._parse()

        self.get = self._Get(self)

    def _parse(self) -> None:
        with open(self.path, encoding="utf-8") as file:
            f = yaml.safe_load(file)
        for name, info in f.items():
            self.as_dict[name] = info
            self._functions.append(
                Function(
                    name=name,
                    description=info.get("description"),
                    returns=map_type(info.get("returns")),
                    parameters=[
                        Parameter(
                            name=param.get("name"),
                            description=param.get("description"),
                            types=map_type(param.get("type")),
                            default=param.get("default"),
                            min_year=param.get("min_year"),
                            options=param.get("options"),
                        )
                        for param in info.get("parameters", {}).values()
                    ],
                )
            )

    class _Get:
        def __init__(self, reader: "YAMLReader") -> None:
            self.reader = reader

        def functions(self) -> list[str]:
            return self.reader._functions

        def function_names(self) -> list[str]:
            return [x.name for x in self.reader._functions]

        def function_info(self, function: str) -> Function:
            return next(f for f in self.reader._functions if f.name == function)
