from nflreadpy import load_rosters
from src.common import Parameters, Utils


if __name__ == "__main__":
    # Init Logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    logger.info(f"Running with parameters: {params.as_dict}")

    # Get rosters
    try:
        logger.info(f"Roster::Getting info for season(s): {params.seasons}")
        rosters = load_rosters(
            seasons=params.seasons
        )
    except Exception as e:
        logger.exception(f"Roster::Exception caught: {e}", e)
    logger.info(f"Roster::Sucess, {params.height} rows of roster info obtained.")

    # Write to table
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    try:
        logger.info(f"Table::Writing roster info to {table_name}")
        spark.createDataFrame(rosters.to_arrow()).write.mode("overwrite").saveAsTable(table_name)
    except Exception as e:
        logger.exception(f"Table::Exception caught: {e}", e)
    logger.info(f"Table::Succsefuly wrote to {table_name}")
