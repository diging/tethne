import networkx as nx
from itertools import combinations

from tethne.utilities import _iterable

def cooccurrence(corpus, attr):
	graph = nx.Graph()
	for paper in corpus.papers:
		for e in combinations(_iterable(getattr(paper, attr)), 2):
			print e
			
		
		
	