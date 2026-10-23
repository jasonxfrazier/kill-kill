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
    summary_levels = ["week", "reg", "post", "reg+post"]

    if isinstance(params.seasons, int):
        rng = range(params.seasons, params.seasons + 1)
    else:
        rng = range(params.seasons[-1], params.seasons[0] - 1, -1)

    # Load, stage, and insert data
    for summary_level in summary_levels:
        if summary_level == "reg+post":
            sum_lvl = "reg_and_post"
        else:
            sum_lvl = summary_level
        for season in rng:
            logger.info(f"Stats::Starting season {season} | Summary level {summary_level}")

            # 1. Load data
            try:
                logger.info(f"Stats::Loading season {season} | Summary level {summary_level}")
                stats = load_player_stats(seasons=[season], summary_level=summary_level)
            except Exception as e:
                raise RuntimeError(
                    f"Stats::LOAD FAILED | {season} | Summary level {summary_level}"
                ) from e

            logger.info(
                f"Stats::SUCCESS loading {season} | Summary level {summary_level} | "
                f"{stats.height:,} rows | {stats.width} columns"
            )

            # 2. Stage data
            staging_path = f"{staging_dir}/{summary_level}_stats_{season}_{sum_lvl}.parquet"

            try:
                logger.info(
                    f"Stats::Staging season {season} | Summary level {summary_level} to {staging_path}"
                )
                stats.write_parquet(staging_path)
            except Exception as e:
                raise RuntimeError(
                    f"Stats::STAGING FAILED | {season} | Summary level {summary_level}"
                ) from e

            logger.info(f"Stats::SUCCESS staging season {season} | Summary level {summary_level}")

            # 3. Read staged data
            try:
                logger.info(
                    f"Stats::Reading staged season {season} | Summary level {summary_level}"
                )
                df = spark.read.parquet(staging_path)  # noqa: F821
            except Exception as e:
                raise RuntimeError(
                    f"Stats::READ FAILED | {season} | Summary level {summary_level}"
                ) from e

            logger.info(f"Stats::SUCCESS reading season {season} | Summary level {summary_level}")

            # 4. Write Delta table
            mode = "overwrite" if season == 2025 else "append"
            try:
                logger.info(
                    f"Table::Writing season {season} | Summary level {summary_level} to {table_name} | Mode: {mode}"
                )
                (
                    df.write.format("delta")
                    .mode(mode)
                    .option("mergeSchema", "true")
                    .saveAsTable(f"{table_name}_{sum_lvl}")
                )
            except Exception as e:
                raise RuntimeError(
                    f"Table::WRITE FAILED | {season} | Summary level {summary_level}"
                ) from e
            logger.info(f"Table::SUCCESS writing season {season}  | Summary level {summary_level}")

    logger.info(f"Stats::SUCCESS | All seasons ingested into {table_name}")
