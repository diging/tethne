from distutils.core import setup

DISTNAME = 'tethne'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('A set of Python modules for constructing graphs from the Web ' +
                'of Science')
LICENSE = 'new BSD' 
URL = 'https://github.com/erickpeirson/tethne' 
VERSION = '0.0.1' 
LONG_DESCRIPTION = open('README.md').read()

setup(name=DISTNAME,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      url=URL,
      version=VERSION,
      long_description=LONG_DESCRIPTION)
