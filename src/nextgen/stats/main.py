from nflreadpy import load_nextgen_stats

from src.common import Parameters, Utils

if __name__ == "__main__":
    # Init logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    logger.info(f"Start::Running with parameters: {params.as_dict}")
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    staging_dir = f"/Volumes/{params.catalog}/{params.schema}/staging"
    stat_types = ["passing", "receiving", "rushing"]

    if isinstance(params.seasons, int):
        rng = range(params.seasons, params.seasons + 1)
    else:
        rng = range(params.seasons[-1], params.seasons[0] + 1, -1)

    # Load, stage, and insert data
    for stat_type in stat_types:
        for season in rng:
            logger.info(f"Next Gen Stats::Starting season {season} | {stat_type}")

            # 1. Load data
            try:
                logger.info(f"Next Gen Stats::Loading season {season} | {stat_type}")
                next_gen = load_nextgen_stats(seasons=[season], stat_type=stat_type)
            except Exception as e:
                raise RuntimeError(f"Next Gen Stats::LOAD FAILED | {season} | {stat_type}") from e

            logger.info(
                f"Next Gen Stats::SUCCESS loading {season} | {next_gen.height:,} rows | {next_gen.width} columns"
            )

            # 2. Stage data
            staging_path = f"{staging_dir}/{stat_type}_next_gen_{season}.parquet"

            try:
                logger.info(f"Next Gen Stats::Staging season {season} to {staging_path}")
                next_gen.write_parquet(staging_path)
            except Exception as e:
                raise RuntimeError(
                    f"Next Gen Stats::STAGING FAILED | {season} | {stat_type}"
                ) from e

            logger.info(f"Next Gen Stats::SUCCESS staging season {season} | {stat_type}")

            # 3. Read staged data
            try:
                logger.info(f"Next Gen Stats::Reading staged season {season} | {stat_type}")
                df = spark.read.parquet(staging_path)  # noqa: F821
            except Exception as e:
                raise RuntimeError(f"Next Gen Stats::READ FAILED | {season} | {stat_type}") from e

            logger.info(f"Next Gen Stats::SUCCESS reading season {season} | {stat_type}")

            # 4. Write Delta table
            mode = "overwrite" if season == 2025 else "append"
            try:
                logger.info(f"Table::Writing season {season} to {table_name} | Mode: {mode}")
                (
                    df.write.format("delta")
                    .mode(mode)
                    .option("mergeSchema", "true")
                    .saveAsTable(f"{table_name}_{stat_type}")
                )
            except Exception as e:
                raise RuntimeError(f"Table::WRITE FAILED | {season} | {stat_type}") from e
            logger.info(f"Table::SUCCESS writing season {season} ")

    logger.info(f"Next Gen Stats::SUCCESS | All seasons ingested into {table_name}")
