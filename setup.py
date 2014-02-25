from distutils.core import setup

DISTNAME = 'tethne'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('Python library for analyzing bibliographic data')
LICENSE = 'GNU GPL 3' 
URL = 'https://github.com/erickpeirson/tethne' 
VERSION = '0.3.1-alpha'
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
      packages = PACKAGES,
      )