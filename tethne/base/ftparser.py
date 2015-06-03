import os
import re

class dobject(object):
	pass

def _cast(value):
	"""
	Attempt to convert ``value`` to an ``int`` or ``float``. If unable, return the value
	unchanged.
	"""

	try:
		return int(value)
	except ValueError:
		try:
			return float(value)
		except ValueError:
			return value
	

class FTParser(object):
	"""
	Base parser for field-tagged data files.
	"""
	
	start_tag = 'ST'
	"""Signals the start of a data entry."""

	end_tag = 'ED'
	"""Signals the end of a data entry."""

	entry_class = dobject
	"""Model for data entry."""
	
	concat_fields = []
	"""Multi-line fields here should be concatenated, rather than represented as lists."""
	
	tags = {}

	def __init__(self, path, **kwargs):
		self.path = path

		self.current_tag = None
		self.last_tag = None
		self.data = []
		self.fields = set([])
		
		self.open()
		
		if kwargs.get('autostart', True):
			self.start()
		
	def open(self):
		"""
		Open the data file.
		"""

		if not os.path.exists(self.path):
			raise IOError("No such path: {0}".format(self.path))
	
		self.buffer = open(self.path, 'r')
	
	def next(self):
		"""
		Get the next line of data.
		
		Returns
		-------
		tag : str
		data : 
		"""
		line = self.buffer.readline()
		while line == '\n':		# Skip forward to the next line with content.
			line = self.buffer.readline()
			
		if line == '':			# End of file.
			return None, None
			
		match = re.match('([A-Z]{2})\W+(.*)', line)
		if match is not None:
			self.current_tag, data = match.groups()
		else:
			self.current_tag = self.last_tag
			data = line.strip()

		return self.current_tag, _cast(data)
		
	def start(self):
		"""
		Find the first data entry and prepare to parse.
		"""

		while self.current_tag != self.start_tag:
			self.next()
		self.new_entry()
			
	def parse(self):
		"""
		
		"""
		while True:		# Main loop.
			tag, data = self.next()
			if tag is None and data is None:	# End of file.
				break

			self.handle(tag, data)
			self.last_tag = tag
		return self.data
					
	def _get_handler(self, tag):
		handler_name = 'handle_{tag}'.format(tag=tag)
		if hasattr(self, handler_name):
			return getattr(self, handler_name)
		return
	
	def __del__(self):
		if hasattr(self, 'buffer'):
			self.buffer.close()
			
	def handle(self, tag, data):
		"""
		Process a single line of data, and store the result.
		
		Parameters
		----------
		tag : str
		data :
		"""

		if data is None or tag is None:
			return
			
		if tag == self.start_tag:
			self.new_entry()
			return	
			
		if tag == self.end_tag:
			self.postprocess_entry()
			return

		handler = self._get_handler(tag)
		if handler is not None:
			data = handler(data)
			
		if tag in self.tags:	# Rename the field.
			tag = self.tags[tag]

		# Multiline fields are represented as lists of values.
		if hasattr(self.data[-1], tag):
			value = getattr(self.data[-1], tag)
			if tag in self.concat_fields:
				value = ' '.join([value, data])
			elif type(value) is list:
				value.append(data)
			elif value not in [None, '']:
				value = [value, data]
		else:
			value = data
		setattr(self.data[-1], tag, value)
		self.fields.add(tag)
		
	def new_entry(self):
		"""
		Prepare a new data entry.
		"""

		self.data.append(self.entry_class())
		
	def postprocess_entry(self):
		for field in self.fields:
			postprocessor_name = 'postprocess_{0}'.format(field)
			if hasattr(self.data[-1], field) and hasattr(self, postprocessor_name):
				getattr(self, postprocessor_name)(self.data[-1])
		
