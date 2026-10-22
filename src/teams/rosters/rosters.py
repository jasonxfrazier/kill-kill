from nflreadpy import load_rosters
from src.common import Parameters


if __name__ == "__main__":
    # Get current params
    params = Parameters.get()
    print(params.as_dict)
    
    Get rosters
    rosters = load_rosters(
        seasons=params.seasons,
        file_type=params.file_type
    )
    print(rosters)

    # Write to table
    # table_name = f"{params['catalog']}.{params['schema']}.{params['table']}"
    # rosters_spark = spark.createDataFrame(rosters.to_pandas())
    # rosters_spark.write.mode("overwrite").saveAsTable(table_name)
    # print(f"Wrote {rosters.height} rows to {table_name}")
