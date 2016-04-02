#!/usr/bin/env python
"""
    A setuptools based setup module.
"""


# Always preser setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

project = 'simple_log_messaging'

"""
packages=find_packages(where='./' + project, 
    include=['runtests.sh', 'test', 'tools', 'lib', 'docs']),
"""

setup_args = dict(
        name=project,
        package_dir={'': './'},
        version='1.0.0',
        description='A simple ZeroMQ based logger for distristributed Raspberry Pi systems',
        url='http://github.com/trailingdots/' + project,
        author='Cecil McGregor',
        author_email='TrailingDots@gmail.com',
        install_requires=['pyzmq', 'zmq'],
        package_data={
            # Misc text files
            '': ['*.conf', '*.data', '*.md', '*.html', '*.css'],
        },
        packages=find_packages(),
        #packages=find_packages(where='./' + project, 
        #    include=['runtests.sh', 'test', 'tools', 'lib', 'docs']),
        scripts = [
            project + '/lib/logCollector',
            project + '/lib/logFilterApp',
            project + '/lib/logCmd',
            project + '/tools/listeningPort'
        ],
        entry_points= {
            'scripts': [
                'logCollector=lib:logCollector',
                'logFilterApp=lib:logFilterApp',
                'logCmd=lib:logCmd',
                'listeningPort=tools:listeningPort'
            ],
            'console_scripts': [
                'logCollector=lib:logCollector',
                'logFilterApp=lib:logFilterApp',
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
