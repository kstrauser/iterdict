#!/usr/bin/env python

from setuptools import setup

setup(
    name="IterDict",
    version="0.1.0",
    author="Kirk Strauser",
    author_email="kirk@strauser.com",
    description=("Dict that lazily populates itself with items from the "
                   "iterator it was constructed with as keys are accessed"),
    license="BSD",
    keywords="dict lazy bigdata",
    url="http://packages.python.org/an_example_pypi_project",
    test_suite='test.test_iterdict',
    py_modules=['iterdict'],
    long_description="""\
IterDicts are almost exactly like regular Python dicts, except that they're
only populated upon demand. This gives them most of the same advantages of
generators, such as the ability to operator on very large (or infinite!)
datasets. For example:

Accessing keys that aren't populated yet

>>> d = IterDict((a, a) for a in xrange(1000000000000000))  # 1 quadrillion (US)
>>> d[10]
10

Deleting keys that aren't populated yet

>>> del d[20]
>>> del d[20]
KeyError: 20
""",
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
