import polars as pl


class Transform:
	numeric_columns = [
		"entry_year",
		"rookie_year",
		"week",
		"draft_number",
		"years_exp",
		"weight",
		"jersey_number",
		"season",
	]

	float_columns = ["height"]

	@classmethod
	def convert_types(cls, df: pl.DataFrame) -> pl.DataFrame:
		schema = df.collect_schema()
		numeric = [c for c in cls.numeric_columns if c in schema]
		floats = [c for c in cls.float_columns if c in schema]
		return df.with_columns(
			pl.col(numeric).cast(pl.Int64, strict=False).fill_null(-1),
			pl.col(floats).cast(pl.Float64, strict=False).fill_null(-1.0),
		)
