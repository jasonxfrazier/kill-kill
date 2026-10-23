from nflreadpy import load_draft_picks

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
        rng = range(params.seasons[-1], params.seasons[0] - 1, -1)

    # Load, stage, and insert data
    for season in rng:
        logger.info(f"Draft Picks::Starting season {season}")

        # 1. Load data
        try:
            logger.info(f"Draft Picks::Loading season {season}")
            draft_picks = load_draft_picks(seasons=[season])
        except Exception as e:
            raise RuntimeError(f"Draft Picks::LOAD FAILED | {season}") from e

        logger.info(
            f"Draft Picks::SUCCESS loading {season} | {draft_picks.height:,} rows | {draft_picks.width} columns"
        )

        # 2. Stage data
        staging_path = f"{staging_dir}/draft_picks_{season}.parquet"

        try:
            logger.info(f"Draft Picks::Staging season {season} to {staging_path}")
            draft_picks.write_parquet(staging_path)
        except Exception as e:
            raise RuntimeError(f"Draft Picks::STAGING FAILED | {season}") from e

        logger.info(f"Draft Picks::SUCCESS staging season {season}")

        # 3. Read staged data
        try:
            logger.info(f"Draft Picks::Reading staged season {season}")
            df = spark.read.parquet(staging_path)  # noqa: F821
        except Exception as e:
            raise RuntimeError(f"Draft Picks::READ FAILED | {season}") from e

        logger.info(f"Draft Picks::SUCCESS reading season {season}")

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

    logger.info(f"Draft Picks::SUCCESS | All seasons ingested into {table_name}")
