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


def map_type(value: str | list[str]) -> type | list[type]:
    return TYPE_MAP.get(value) if isinstance(value, str) else [TYPE_MAP.get(x) for x in value]
