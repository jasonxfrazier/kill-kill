from common import NFLReader, YAMLReader, JobReader


if __name__ == "__main__":
    # Job Parameters
    job = JobReader()

    # Initialize NFLReader
    nfl = NFLReader(YAMLReader("functions.yml"))

    # Extract relavent parameters
    function_name = job.parameters["function"]
    function_info = nfl.config.get.function_info(function_name)
    allowed = {param.name for param in function_info.parameters}
    kwargs = {
        k: v
        for k, v in job.parameters.items()
        if k in allowed
    }

    # Excecute function
    df = nfl.function(function_name, **kwargs)
