import sys

class Error:

	def __init__(self, message : str, exit_code : int = 1, exit : bool = False):
		self.message = message
		self.exit_code = exit_code
		self.exit = exit
		self.do_error()

	def do_error(self):
		print(f'error: {self.message}')
		if self.exit is True:
			sys.exit(self.exit_code)

	
