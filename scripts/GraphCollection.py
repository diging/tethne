import tethne.readers as rd
data = rd.wos.read("/Users/ramki/tethne/testsuite/testin/test_c1.txt")
data = rd.wos.read("/Users/ramki/tethne/testsuite/testin/tissues.txt")
from tethne.data import DataCollection
D = DataCollection(data) # Indexed by wosid, by default.
D.slice('date', 'time_window', window_size=4)
from tethne.builders import authorCollectionBuilder
builder = authorCollectionBuilder(D)
C = builder.build('date', 'coauthors')
C
        