import ast
import logging
import sys
from typing import Any


class Utils:
	"""
	Contains general utility methods.
	Usage Ex:
	Utils.infer_type_from_string("some string")
	"""

	@staticmethod
	def infer_type_from_string(value: str) -> Any:
		"""
		Will infer a strings type and return it in its type correct form.
		"""
		if value == "true":
			return True
		if value == "false":
			return False
		if value in ["null", "Null", "none"]:
			return -1
		try:
			val = ast.literal_eval(value)
			if isinstance(val, list):
				return [Utils.infer_type_from_string(v) if isinstance(v, str) else v for v in val]
			if isinstance(val, dict):
				return {
					k: Utils.infer_type_from_string(v) if isinstance(v, str) else v
					for k, v in val.items()
				}
			return val
		except (ValueError, SyntaxError, TypeError):
			return value

	@staticmethod
	def logger(name: str) -> logging.Logger:
		"""
		Python logging wrapper.
		"""
		logger = logging.getLogger(name)
		logger.setLevel(logging.INFO)
		if not logger.handlers:
			handler = logging.StreamHandler(sys.stdout)
			formatter = logging.Formatter(
				fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
				datefmt="%Y-%m-%d %H:%M:%S",
			)
			handler.setFormatter(formatter)
			logger.addHandler(handler)
		logger.propagate = False
		return logger
