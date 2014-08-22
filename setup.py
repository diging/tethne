from distutils.core import setup

DISTNAME = 'tethne'
AUTHOR = 'E. Peirson, Digital Innovation Group @ ASU'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('Bibliographic network and corpus analysis for historians')
LICENSE = 'GNU GPL 3' 
URL = 'http://diging.github.io/tethne/'
<<<<<<< HEAD
VERSION = '0.6.1-beta'
=======
VERSION = '0.6.2-beta'
>>>>>>> c9995a4e3bdcee8d8bdecc731621bb27394cbcdb
PACKAGES = [ 'tethne',
             'tethne.analyze',
             'tethne.classes', 
             'tethne.model',
             'tethne.model.corpus',
             'tethne.model.managers',
             'tethne.model.social',                          
             'tethne.networks',
             'tethne.persistence',
             'tethne.persistence.hdf5',                          
             'tethne.readers',
             'tethne.services',
             'tethne.utilities', 
             'tethne.writers', 
            ]

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
    install_requires=[
        "networkx >= 1.8.1",
        "matplotlib >= 1.3.1",
        "tables >= 3.1.1",
        "Unidecode >= 0.04.16",
        "geopy >= 0.99",
        "nltk",
        "scipy==0.14.0",
        "numpy==1.8.1",
    ],
)