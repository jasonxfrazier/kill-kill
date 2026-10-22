from databricks.sdk.runtime import dbutils as dbx

from src.common.utils import Utils


class Parameters:
	"""
	Contains Environment Varables.
	Usage:
	parameters = Parameters.get()
	parameters.expected_parameter
	parameters.as_dict
	"""

	def __init__(self):
		self.as_dict = {}

	@classmethod
	def get(cls):
		instance = cls()
		for key, value in dbx.widgets.getAll().items():
			parsed = Utils.infer_type_from_string(value)
			setattr(instance, key, parsed)
			instance.as_dict[key] = parsed
		return instance
