#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-paramark',
    version='0.1.0',
    author='Michał Lowas-Rzechonek',
    author_email='michal@rzechonek.net',
    maintainer='Michał Lowas-Rzechonek',
    maintainer_email='michal@rzechonek.net',
    license='MIT',
    url='https://github.com/mrzechonek/pytest-paramark',
    description=(
        'Configure pytest fixtures using a combination of'
        '"parametrize" and markers'
    ),
    long_description=read('README.rst'),
    py_modules=['pytest_paramark'],
    python_requires='>=3.4',
    setup_requires=['pytest-runner>=4.2'],
    install_requires=['pytest>=4.5.0'],
    tests_require=['namedlist'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'paramark = pytest_paramark',
        ],
    },
)
