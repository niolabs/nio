import re
from setuptools import setup, find_packages

with open('nio/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='nio',
    description='A framework for building blocks for n.io',
    keywords=['nio', 'n.io'],
    version=version,
    packages=find_packages(
        exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),

    # No dependenices, believe it!
    install_requires=[],

    tests_require=[
        'requests>=2.3.0'
    ],

    author='n.io',
    author_email='info@n.io',
    url='http://n.io'
)
