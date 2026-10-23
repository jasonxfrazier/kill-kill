from nflreadpy import load_player_stats

from src.common import Parameters, Utils

if __name__ == "__main__":
    # Init logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    logger.info(f"Start::Running with parameters: {params.as_dict}")
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    staging_dir = f"/Volumes/{params.catalog}/{params.schema}/staging"
    
    if isinstance(params.seasons, int):
        rng = range(params.seasons, params.seasons + 1)
    else:
        rng = range(params.seasons[-1], params.seasons[0], -1)
    
    # Load, stage, and insert data
    for season in rng:
        logger.info(f"Stats::Starting season {season}")

        # 1. Load data
        try:
            logger.info(f"Stats::Loading season {season}")
            stats = load_player_stats(seasons=[season])
        except Exception as e:
            logger.exception(f"Stats::FAILED loading season {season}")
            raise RuntimeError(f"Stats::LOAD FAILED | {season}") from e

        logger.info(
            f"Stats::SUCCESS loading {season} | "
            f"{stats.height:,} rows | {stats.width} columns"
        )

        # 2. Stage data
        staging_path = f"{staging_dir}/stats_{season}.parquet"

        try:
            logger.info(f"Stats::Staging season {season} to {staging_path}")
            stats.write_parquet(staging_path)
        except Exception as e:
            logger.exception(f"Stats::FAILED staging season {season}")
            raise RuntimeError(f"Stats::STAGING FAILED | {season}") from e

        logger.info(f"Stats::SUCCESS staging season {season}")

        # 3. Read staged data
        try:
            logger.info(f"Stats::Reading staged season {season}")
            df = spark.read.parquet(staging_path)  # noqa: F821
        except Exception as e:
            logger.exception(f"Stats::FAILED reading season {season}")
            raise RuntimeError(f"Stats::READ FAILED | {season}") from e

        logger.info(f"Stats::SUCCESS reading season {season}")

        # 4. Write Delta table
        mode = "overwrite" if season == 2025 else "append"

        try:
            logger.info(
                f"Table::Writing season {season} to {table_name} | Mode: {mode}"
            )
            (
                df.write
                .format("delta")
                .mode(mode)
                .option("mergeSchema", "true")
                .saveAsTable(table_name)
            )
        except Exception as e:
            raise RuntimeError(f"Table::WRITE FAILED | {season}") from e
        logger.info(f"Table::SUCCESS writing season {season}")

    logger.info(f"Stats::SUCCESS | All seasons ingested into {table_name}")
