from distutils.core import setup

DISTNAME = 'tethne'
AUTHOR = 'E. Peirson, Digital Innovation Group @ ASU'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('Bibliographic network and corpus analysis for historians')
LICENSE = 'GNU GPL 3'
URL = 'http://diging.github.io/tethne/'
VERSION = '0.8'

PACKAGES = ['tethne',
            'tethne.analyze',
            'tethne.classes',
            'tethne.model',
            'tethne.model.corpus',
            'tethne.networks',
            'tethne.readers',
            'tethne.writers']

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
        "Unidecode >= 0.04.16",
        "iso8601",
        "rdflib",
        "codecs",
        "cchardet",
        "unicodedata"
    ],
)
