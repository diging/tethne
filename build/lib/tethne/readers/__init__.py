"""
Contains methods for parsing bibliographic datasets.
"""

import wos
import bibtex
import pubmed

class DataError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)