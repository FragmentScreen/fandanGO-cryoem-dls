from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Load requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='fandanGO-cryoem-dls',
    version='0.1.0',
    description='Diamond Light Source cryo-EM plugin for FandanGO application',
    long_description=long_description,
    author='Diamond Light Source',
    author_email='scientificsoftware@diamond.ac.uk',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'fandango.plugin': 'fandanGO-cryoem-dls = fandango_dls'
    },
)
