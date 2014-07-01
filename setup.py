from distutils.core import setup

DISTNAME = 'Tethne'
AUTHOR = 'E. Peirson, Digital Innovation Group @ ASU'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('Bibliographic network and corpus analysis for historians')
LICENSE = 'GNU GPL 3' 
URL = 'https://github.com/diging/tethne'
VERSION = '0.5.0-dev'
PACKAGES = [ 'tethne','tethne.analyze','tethne.networks','tethne.readers',
             'tethne.utilities', 'tethne.writers', 'tethne.model',
             'tethne.services', 'tethne.classes' ]

setup(
    name=DISTNAME,
    author=AUTHOR,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    version=VERSION,
    packages = PACKAGES,
    long_description=open('README.md').read(),
    install_requires=[
        "networkx >= 1.8.1",
        "matplotlib >= 1.3.1",
        "tables >= 3.1.1",
        "Unidecode >= 0.04.16",
        "geopy >= 0.99",
        "nltk",
    ],
)