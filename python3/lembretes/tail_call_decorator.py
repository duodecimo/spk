#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from sys import _getframe

except ImportError:
	import sys
	
	try:
		raise Exception
	
	except:
		if (
			not hasattr(sys.exc_info()[2], 'tb_frame') or
			not hasattr(sys.exc_info()[2].tb_frame, 'f_back')
		):
			raise ImportError(
				"Unable to capture frames. sys._getframe() is not supported "
				"in this Python implementation, and the traceback object does "
				"not conform to CPython specifications."
			)
		
		else:
			def _getframe(level=0):
				"""
				A reimplementation of `sys._getframe()`. `level` is the number
				of levels deep into the stack to grab the frame from
				(default: 0).
				
				`_getframe()` is a private function, and isn't guaranteed to
				exist in all versions and implementations of Python. This
				function is about 2x slower.
				
				`sys.exc_info()` only returns helpful information if an
				exception has been raised.
				
				"""
				
				try:
					raise Exception
				
				except:
					# sys.exc_info() returns (type, value, traceback).
					frame = sys.exc_info()[2].tb_frame
					
					# + 1 to account for our exception.
					for i in xrange(0, level + 1):
						frame = frame.f_back
				
				finally:
					sys.exc_clear()
				
				return frame
	
	finally:
		sys.exc_clear()


class TailCallSigil(Exception):
	def __init__(self, args, kwargs):
		self.args = args
		self.kwargs = kwargs


def tail_call(function):
	"""
	A decorator for functions set up for tail call optimization. If your
	function *isn't* set up for tail call optimization, this won't work
	as intended.
	
	You should probably never use this.
	
	(Mutually recursive functions work, so long as all functions have the
	`@tail_call` decorator.)
	
	"""
	
	def wrapper(*args, **kwargs):
		"""
		Wraps a function optimized for tail calls, allowing them to reuse the
		stack.
		
		"""
		
		try:
			# Check to make sure we aren't our own grandparent.
			frame_0, frame_2 = _getframe(0), _getframe(2)
			
			if frame_2 and frame_0.f_code == frame_2.f_code:
				raise TailCallSigil(args, kwargs)
		
		except ValueError:
			pass
		
		while True:
			try:
				# Will be called decorated, hence the grandparents above.
				result = function(*args, **kwargs)
			
			except TailCallSigil as sigil:
				args, kwargs = sigil.args, sigil.kwargs
			
			else:
				return result
	
	return wrapper


if __name__ == '__main__':
	import sys
	
	@tail_call
	def tail_factorial(n, current=1):
		"""
		Factorial function designed for tail recursion.
		
		"""
		
		if n == 1:
			return current
		
		else:
			return tail_factorial(n - 1, current * n)
	
	# Python's recursion limit is usually 1000.
	print(tail_factorial(sys.getrecursionlimit() * 10))

