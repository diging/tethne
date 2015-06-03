"""
A :class:`.Paper` represents a single document. :class:`.Paper` objects behave
much like conventional Python dictionaries, except that they are picky about
the kind of data that you throw into them.
"""


class Paper(object):
	"""
	Tethne's representation of a bibliographic record.
	"""

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def __getitem__(self, key):
		return getattr(self, key)

	@property
	def authors(self):
		"""
		Get the authors of the current :class:`.Paper` instance.

		Returns
		-------
		authors : list
			Author names are in the format ``LAST F``. If there are no authors,
			returns an empty list.
		"""

		if hasattr(self, 'authors_full'):
			return self.authors_full
		elif hasattr(self, 'authors_init'):
			return self.authors_init
		else:
			return []
