#!/usr/bin/env python
"""
    A setuptools based setup module.
"""


# Always preser setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup_args = dict(
        name='simple_log_messaging',
        version='1.0.0',
        description='A simple ZeroMQ based logger for distristributed Raspberry Pi systems',
        url='http://github.com/trailingdots/simple_log_messaging',
        author='Cecil McGregor',
        author_email='TrailingDots@gmail.com',
        install_requires=['pyzmq', 'zmq'],
        packages=find_packages(exclude=['test', 'doc', 'examples']),
        entry_points= {
            'console_scripts': [
                'logCollector=lib:logCollector',
                'loggingFilterApp=lib:loggingFilterApp',
                'logCmd=lib:logCmd',
                'listeningPort=tools:listeningPort'
            ]
        },
        zip_safe=False,
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
