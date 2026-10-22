from nflreadpy import load_rosters

from src.common import Parameters, Utils
from src.teams.rosters.transform import Transform

if __name__ == "__main__":
	# Init logging
	logger = Utils.logger(__name__)

	# Get current params
	params = Parameters.get()
	logger.info(f"Start::Running with parameters: {params.as_dict}")

	# Get rosters
	try:
		logger.info(f"Roster::Getting info for season(s): {params.seasons}")
		rosters = load_rosters(seasons=params.seasons)
	except Exception as e:
		raise RuntimeError("Roster::FAILED") from e
	logger.info(f"Roster::SUCCESS, {rosters.height} rows of roster info obtained.")

	# Write to bronze table
	table_name = f"{params.catalog}.{'bronze'}.{params.table}"
	try:
		logger.info(f"Bronze-Table::Writing roster info to {table_name}")
		spark.createDataFrame(rosters.to_arrow()).write.mode("overwrite").saveAsTable(table_name)  # noqa: F821
	except Exception as e:
		raise RuntimeError("Bronze-Table::FAILED") from e
	logger.info(f"Bronze-Table::SUCCESS, wrote to {table_name}")

	# Clean up
	try:
		logger.info("Transform::Standardizing column types.")
		rosters = Transform.convert_types(rosters)
	except Exception as e:
		raise RuntimeError("Transform::FAILED") from e
	logger.info("Transform::SUCCESS")

	# Write to silver table
	table_name = f"{params.catalog}.{'silver'}.{params.table}"
	try:
		logger.info(f"Bronze-Table::Writing roster info to {table_name}")
		spark.createDataFrame(rosters.to_arrow()).write.mode("overwrite").saveAsTable(table_name)  # noqa: F821
	except Exception as e:
		raise RuntimeError("Bronze-Table::FAILED") from e
	logger.info(f"Bronze-Table::SUCCESS, wrote to {table_name}")
