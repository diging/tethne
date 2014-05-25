import unittest

import __builtin__
__builtin__.datapath = './refactor/data'

import sys
sys.path.append('../')

from test_classes_datacollection import *
from test_classes_graphcollection import *
from test_classes_modelcollection import *
from test_classes_paper import *

if __name__ == '__main__':
    unittest.main()