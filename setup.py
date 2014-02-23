from distutils.core import setup

DISTNAME = 'tethne'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('A set of Python modules for constructing graphs from the Web ' \
                + 'of Science')
LICENSE = 'GNU GPL 3' 
URL = 'https://github.com/erickpeirson/tethne' 
VERSION = '0.3'
LONG_DESCRIPTION = open('README.md').read()
PACKAGES = [ 'tethne','tethne.analyze','tethne.networks','tethne.readers', \
             'tethne.utilities', 'tethne.writers', 'tethne.matrices',
             'testsuite' ]

setup(name=DISTNAME,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      url=URL,
      version=VERSION,
      long_description=LONG_DESCRIPTION,
      packages = PACKAGES,
      install_requires = ['networkx >= 1.8']
      )