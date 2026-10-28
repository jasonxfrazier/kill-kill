from delta.tables import DeltaTable
from pyspark.sql import functions as F  # noqa: N812

from common import JobReader, NFLReader, YAMLReader, logger

log = logger(__name__)

if __name__ == "__main__":
    # Job Parameters
    job = JobReader()
    params = job.parameters
    job_name = params.get("job_name")
    if not job_name:
        log.exception("Unable to Read")
        raise ValueError("Missing 'job_name' parameter")
    log.info("Job: %s | Starting", job_name)

    # Check required
    log.info("%s::Checking Required Parameters", job_name)
    try:
        if not params.get("catalog"):
            raise ValueError("Missing Required Job Parameter: 'catalog'")
        if not params.get("schema"):
            raise ValueError("Missing Required Job Parameter: 'schema'")
        if not params.get("table"):
            raise ValueError("Missing Required Job Parameter: 'table'")
        if not params.get("catalog"):
            raise ValueError("Missing Required Job Parameter: 'function'")
    except Exception:
        log.exception("%s::Checking Required Parameters::FAIL", job_name)
        raise
    log.info("%s::Checking Required Parameters::SUCCESS", job_name)

    # Initialize Readers
    log.info("%s::Initializing YAMLReader", job_name)
    try:
        yaml_reader = YAMLReader("functions.yml")
    except Exception:
        log.exception("%s::Initializing YAMLReader::FAIL", job_name)
        raise
    log.info("%s::Initializing YAMLReader::SUCCESS", job_name)
    log.info("%s::Initializing NFLReader", job_name)
    try:
        nfl = NFLReader(yaml_reader)
    except Exception:
        log.exception("%s::Initializing NFLReader::FAIL", job_name)
        raise
    log.info("%s::Initializing NFLReader::SUCCESS", job_name)

    # Extract relavent parameters
    try:
        function_name = params.get("function")
        function_info = nfl.config.get.function_info(function_name)
        allowed = {param.name for param in function_info.parameters}
        kwargs = {k: v for k, v in params.items() if k in allowed}
        staging_path = f"/Volumes/{params.get('catalog')}/{params.get('schema')}/staging/{params.get('table')}.parquet"
        table_path = f"{params.get('catalog')}.{params.get('schema')}.{params.get('table')}"
    except Exception:
        log.exception("%s::Getting Paths::FAIL", job_name)
        raise
    log.info("%s::Getting Paths::SUCCESS", job_name)

    # Excecute function
    log.info("%s::Execute %s", job_name, function_name)
    try:
        df = nfl.function(function_name, **kwargs)
    except Exception:
        log.exception("%s::Execute %s::FAIL", job_name, function_name)
        raise
    log.info("%s::Execute %s::SUCCESS", job_name, function_name)

    # Stage data as parquet
    log.info("%s::Staging Data at: %s", job_name, staging_path)
    try:
        df.write_parquet(staging_path)
    except Exception:
        log.exception("%s::Staging Data::FAIL", job_name)
        raise
    log.info("%s::Staging Data::SUCCESS", job_name)

    # Read into spark
    log.info("%s::Reading to Spark DF", job_name)
    try:
        spark_df = spark.read.parquet(staging_path)  # noqa: F821
    except Exception:
        log.exception("%s::Reading to Spark DF::FAIL", job_name)
        raise
    log.info("%s::Reading to Spark DF::SUCCESS", job_name)

    # Generate row IDs
    log.info("%s::Generating Row IDs", job_name)
    columns = sorted(spark_df.columns)
    spark_df = spark_df.withColumn(
        "row_hash",
        F.sha2(
            F.to_json(F.struct(*[F.col(c) for c in columns])),
            256,
        ),
    )
    log.info("%s::Generating Row IDs::SUCCESS", job_name)

    # Write to table
    log.info("%s::Writing to Table at: %s", job_name, table_path)
    if not spark.catalog.tableExists(table_path):  # noqa: F821
        spark_df.write.format("delta").mode("append").saveAsTable(table_path)
    target = DeltaTable.forName(spark, table_path)  # noqa: F821
    target_aliased = target.alias("target")
    source_aliased = spark_df.alias("source")
    target_columns = set(target.toDF().columns)
    source_columns = set(spark_df.columns)
    insert_columns = target_columns & source_columns
    insert_values = {col: f"source.`{col}`" for col in insert_columns}
    try:
        (
            target_aliased.merge(
                source_aliased,
                "target.row_hash = source.row_hash",
            )
            .whenNotMatchedInsert(values=insert_values)
            .execute()
        )
    except Exception:
        log.exception("%s::Writing to Table::FAIL", job_name)
        raise
    log.info("%s::Writing to Table::SUCCESS", job_name)

    log.info("Job: %s | Done", job_name)
