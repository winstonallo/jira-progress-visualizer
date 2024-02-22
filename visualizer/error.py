import sys

class Error:

	def __init__(self, message : str, exit_code : int = 1):
		self.message = message
		self.do_error()
		self.exit_code = exit_code

	def do_error(self):
		print(self.message)
		sys.exit(self.exit_code)

	
