from nflreadpy import load_rosters
from src.common import Parameters, Utils


if __name__ == "__main__":
    # Init Logging
    logger = Utils.logger(__name__)

    # Get current params
    params = Parameters.get()
    print(params.as_dict)

    # Get rosters
    rosters = load_rosters(
        seasons=params.seasons,
    )
    print(rosters)

    # Write to table
    table_name = f"{params.catalog}.{params.schema}.{params.table}"
    spark.createDataFrame(rosters.to_arrow()).write.mode("overwrite").saveAsTable(table_name)
