from tethne.managers import SampleDFRManager, GenericGraphCollectionManager
datapath = '/Users/erickpeirson/tethne/testsuite/refactor/data/dfr'
MN = SampleDFRManager(datapath)
MN.run()

GM = GenericGraphCollectionManager(MN.D, 'date', 'authors', 'coauthors')
GM.run()