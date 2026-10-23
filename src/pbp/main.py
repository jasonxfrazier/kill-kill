from nflreadpy import load_pbp

from src.common import Parameters, Utils

if __name__ == "__main__":
    # Init logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    logger.info(f"Start::Running with parameters: {params.as_dict}")

    # Get pbps
    try:
        logger.info(f"PBP::Getting info for season(s): {params.seasons}")
        pbp = load_pbp(seasons=params.seasons)
    except Exception as e:
        raise RuntimeError("PBP::FAILED") from e
    logger.info(f"PBP::SUCCESS, {pbp.height} rows of pbp info obtained.")

    # Write to table
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    try:
        logger.info(f"Table::Writing pbp info to {table_name}")
        spark.createDataFrame(pbp.to_arrow()).write.mode("overwrite").saveAsTable(table_name)  # noqa: F821
    except Exception as e:
        raise RuntimeError("Table::FAILED") from e
    logger.info(f"Table::SUCCESS, wrote to {table_name}")
