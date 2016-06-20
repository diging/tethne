from setuptools import setup, Extension

DISTNAME = 'tethne'
AUTHOR = 'E. Peirson, Digital Innovation Group @ ASU'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('Bibliographic network and corpus analysis for historians')
LICENSE = 'GNU GPL 3'
URL = 'http://diging.github.io/tethne/'
VERSION = '0.7.30'

PACKAGES = ['tethne',
            'tethne.analyze',
            'tethne.classes',
            'tethne.model',
            'tethne.model.corpus',
            'tethne.networks',
            'tethne.readers',
            'tethne.writers',
            'tethne.plot']

import sys
if sys.version_info[0] == 2:
    pdfminer = 'pdfminer==20140328'
elif sys.version_info[0] == 3:
    pdfminer = "pdfminer3k"


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
    include_package_data=True,
    install_requires=[
        "networkx >= 1.8.1",
        "Unidecode >= 0.04.16",
        "iso8601",
        "rdflib",
        "chardet",
        "html5lib",
        "isodate",
        "pdfdocument",
        pdfminer,
        "python-magic==0.4.6",
        "slate",
        "Unidecode==0.4.17",
        "nltk",
    ],
)
