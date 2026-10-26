import nflreadpy
import polars as pl

from src.common.readers.yaml.reader import YAMLReader


class NFLReader:
    """
    Takes `YAMLReader` object & orchestrates `nflreadpy` functions.
    Initialize:
    \treader = NFLReader('path/to/file.yaml')
    Attributes:
    \treader.config
    Methods:
    \treader.function()
    """

    def __init__(self, config: YAMLReader) -> None:
        self.config = config

    def function(self, function_name: str, **kwargs) -> pl.DataFrame:
        func = getattr(nflreadpy, function_name)
        return func(**kwargs)
