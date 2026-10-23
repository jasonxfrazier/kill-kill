from nflreadpy import load_schedules

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
        rng = range(params.seasons[-1], params.seasons[0] + 1, -1)

    # Load, stage, and insert data
    for season in rng:
        logger.info(f"Schedules::Starting season {season}")

        # 1. Load data
        try:
            logger.info(f"Schedules::Loading season {season}")
            schedules = load_schedules(seasons=[season])
        except Exception as e:
            raise RuntimeError(f"Schedules::LOAD FAILED | {season}") from e

        logger.info(
            f"Schedules::SUCCESS loading {season} | "
            f"{schedules.height:,} rows | {schedules.width} columns"
        )

        # 2. Stage data
        staging_path = f"{staging_dir}/schedules_{season}.parquet"

        try:
            logger.info(f"Schedules::Staging season {season} to {staging_path}")
            schedules.write_parquet(staging_path)
        except Exception as e:
            raise RuntimeError(f"Schedules::STAGING FAILED | {season}") from e

        logger.info(f"Schedules::SUCCESS staging season {season}")

        # 3. Read staged data
        try:
            logger.info(f"Schedules::Reading staged season {season}")
            df = spark.read.parquet(staging_path)  # noqa: F821
        except Exception as e:
            raise RuntimeError(f"Schedules::READ FAILED | {season}") from e

        logger.info(f"Schedules::SUCCESS reading season {season}")

        # 4. Write Delta table
        mode = "overwrite" if season == 2025 else "append"
        try:
            logger.info(f"Table::Writing season {season} to {table_name} | Mode: {mode}")
            (
                df.write.format("delta")
                .mode(mode)
                .option("mergeSchema", "true")
                .saveAsTable(f"{table_name}")
            )
        except Exception as e:
            raise RuntimeError(f"Table::WRITE FAILED | {season}") from e
        logger.info(f"Table::SUCCESS writing season {season} ")

    logger.info(f"Schedules::SUCCESS | All seasons ingested into {table_name}")
