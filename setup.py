#!/usr/bin/env python
"""
    A setuptools based the setup module.
"""


# Always preser setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

project = 'simple_log_messaging'

setup_args = dict(
        name=project,
        package_dir={'': './'},
        version='1.0.0',
        description='A simple ZeroMQ based logger for distributed Raspberry Pi systems',
        url='http://github.com/trailingdots/' + project,
        author='Trailing Dots',
        author_email='TrailingDots@gmail.com',
        install_requires=['pyzmq', 'zmq'],
        package_data={
            '': ['*.conf', '*.data', '*.md', '*.html', '*.css'],
        },
        packages=find_packages(exclude=['*.test', 'test', '*tools', 'tools']),
        entry_points= {
            'console_scripts': [
                'module=module',
                'logCollector=logCollector:main',
                'logFilterApp=logFilterApp:main',
                'logCmd=logCmd:main',
                'listeningPort=listeningPort:main'
            ]
        },
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
        ],
)

setup(**setup_args)
