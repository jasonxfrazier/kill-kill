import polars as pl

TYPE_MAP = {
    "int": int,
    "str": str,
    "string": str,
    "bool": bool,
    "float": float,
    "None": type(None),
    "polars.DataFrame": pl.DataFrame,
}


def map_type(value: str | list[str]) -> object | list[type]:
    """Converts string respresentation of types to valid python types."""
    return TYPE_MAP.get(value) if isinstance(value, str) else [TYPE_MAP.get(x) for x in value]
