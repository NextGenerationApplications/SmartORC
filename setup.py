# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "dynamic_orchestrator"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="OpenApi 3.0 ReST interface for Accordion Orchestrator",
    author_email="",
    url="",
    keywords=["Swagger", "OpenApi 3.0 ReST interface for Accordion Orchestrator"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['dynamic_orchestrator=dynamic_orchestrator.__main__:main']},
    long_description="""\
    This is the Yaml file that goes with our server code
    """
)
