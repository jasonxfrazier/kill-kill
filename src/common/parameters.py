from databricks.sdk.runtime import dbutils
from typing import Dict, List


class Parameters:
    def __init__(self):
        self.args = dbutils.widgets.getAll()

    # Public
    def get_args(self, parameters: List[str]) -> Dict[str, str]:
        return self.args