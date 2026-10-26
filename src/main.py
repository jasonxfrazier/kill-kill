from common import JobReader, NFLReader, YAMLReader

if __name__ == "__main__":
    # Job Parameters
    job = JobReader()
    params = job.parameters

    # Check required
    if not params.get("catalog"):
        raise ValueError("Missing Required Job Parameter: 'catalog'")
    if not params.get("schema"):
        raise ValueError("Missing Required Job Parameter: 'schema'")
    if not params.get("table"):
        raise ValueError("Missing Required Job Parameter: 'table'")
    if not params.get("catalog"):
        raise ValueError("Missing Required Job Parameter: 'function'")

    # Initialize NFLReader
    nfl = NFLReader(YAMLReader("functions.yml"))

    # Extract relavent parameters
    function_name = params.get("function")
    function_info = nfl.config.get.function_info(function_name)
    allowed = {param.name for param in function_info.parameters}
    kwargs = {k: v for k, v in params.items() if k in allowed}
    staging_path = f"/Volumes/{params.get('catalog')}/{params.get('schema')}/staging/{params.get('table')}.parquet"
    table_path = f"{params.get('catalog')}.{params.get('schema')}.{params.get('table')}"

    # Excecute function
    df = nfl.function(function_name, **kwargs)

    # Stage data as parquet
    df.write_parquet(staging_path)

    # Read into spark
    spark_df = spark.read.parquet(staging_path)  # noqa: F821

    # Write to table
    spark_df.write.format("delta").mode("overwrite").saveAsTable(table_path)
