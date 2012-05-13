#!/usr/bin/env python

from setuptools import setup, find_packages


def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="IterDict",
    version="0.2.0",
    author="Kirk Strauser",
    author_email="kirk@strauser.com",
    description=("Dict that lazily populates itself with items from the "
                   "iterator it was constructed with as keys are accessed"),
    license="BSD",
    keywords="dict lazy bigdata",
    url="http://packages.python.org/an_example_pypi_project",
    test_suite='iterdict.test.test_iterdict',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    long_description=read('README.markdown'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: BSD License",
    ],
)
