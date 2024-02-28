import sys

class Error:

	def __init__(self, message : str, exit_code : int = 1):
		self.message = message
		self.exit_code = exit_code
		self.do_error()

	def do_error(self, exit : bool = False):
		print(f'error: {self.message}')
		if exit is True:
			sys.exit(self.exit_code)

	
