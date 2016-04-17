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
        description='A simple python-based ZeroMQ based logger for distributed Raspberry Pi systems',
        url='http://github.com/trailingdots/' + project,
        author='Trailing Dots',
        keywords='ZeroMQ 0mq distributed networking messaging socket client server p2p publish subscribe requrest reply push pull backend microservices python',
        author_email='TrailingDots@gmail.com',
        install_requires=['pyzmq', 'zmq'],
        namespace_packages=[],
        zip_safe=False,
        package_data={
            '': ['*.conf', '*.data', '*.md', '*.html', '*.css'],
        },
        packages=find_packages(exclude=['*.test', 'test', '*tools', 'tools']),
        include_package_data=True,
        py_modules=['simple_log_messaging'],
        scripts=[
            'logCollector=simple_log_messaging.simple_log_messaging.bin.logCollector',
            'logFilterApp=simple_log_messaging.simple_log_messaging.bin.logFilterApp',
            'logCmd=simple_log_messaging.simple_log_messaging.logCmd.bin:logCmd',
            'listeningPort=simple_log_messaging.simple_log_messaging.bin.listeningPort'
        ],
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

print 'packages:%s' % str(setup_args['packages'])

setup(**setup_args)
