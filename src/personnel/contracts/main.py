from nflreadpy import load_contracts

from src.common import Parameters, Utils

if __name__ == "__main__":
    # Init logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    logger.info(f"Start::Running with parameters: {params.as_dict}")
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    staging_dir = f"/Volumes/{params.catalog}/{params.schema}/staging"

    # Load, stage, and insert data
    logger.info("Contracts::Starting")

    # 1. Load data
    try:
        logger.info("Contracts::Loading")
        contracts = load_contracts()
    except Exception as e:
        raise RuntimeError("Contracts::LOAD FAILED") from e

    logger.info(
        f"Contracts::SUCCESS loading  | {contracts.height:,} rows | {contracts.width} columns"
    )

    # 2. Stage data
    staging_path = f"{staging_dir}/contracts.parquet"

    try:
        logger.info(f"Contracts::Staging to {staging_path}")
        contracts.write_parquet(staging_path)
    except Exception as e:
        raise RuntimeError("Contracts::STAGING FAILED") from e

    logger.info("Contracts::SUCCESS staging")

    # 3. Read staged data
    try:
        logger.info("Contracts::Reading staged")
        df = spark.read.parquet(staging_path)  # noqa: F821
    except Exception as e:
        raise RuntimeError("Contracts::READ FAILED | ") from e

    logger.info("Contracts::SUCCESS reading")

    # 4. Write Delta table
    try:
        logger.info(f"Table::Writing to {table_name} | Mode: append")
        (
            df.write.format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .saveAsTable(f"{table_name}")
        )
    except Exception as e:
        raise RuntimeError("Table::WRITE FAILED") from e
    logger.info("Table::SUCCESS writing")
