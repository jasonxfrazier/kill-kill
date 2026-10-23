from nflreadpy import load_players

from src.common import Parameters, Utils

if __name__ == "__main__":
    # Init logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    logger.info(f"Start::Running with parameters: {params.as_dict}")

    # Get players
    try:
        logger.info("Players::Getting player info")
        players = load_players()
    except Exception as e:
        raise RuntimeError("Players::FAILED") from e
    logger.info(f"Players::SUCCESS, {players.height} rows of player info obtained.")

    # Write to table
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    try:
        logger.info(f"Table::Writing roster info to {table_name}")
        spark.createDataFrame(players.to_arrow()).write.mode("overwrite").saveAsTable(table_name)  # noqa: F821
    except Exception as e:
        raise RuntimeError("Table::FAILED") from e
    logger.info(f"Table::SUCCESS, wrote to {table_name}")
