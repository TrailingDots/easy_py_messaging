"""
    A setuptools based setup module.
"""
# Prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

project = 'easy_py_messaging'

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
    zip_safe=False,
    package_data={
        '': ['*.conf', '*.data', '*.md', '*.html', '*.css'],
    },
    packages=find_packages(exclude=['*.test', 'test', '*tools', 'tools']),
    include_package_data=True,
    scripts = [
        'easy_py_messaging/bin/logCollector',
        'easy_py_messaging/bin/logCmd',
        'easy_py_messaging/bin/listeningPort',
        'easy_py_messaging/bin/listening',
        'easy_py_messaging/bin/logFilterApp',
        'easy_py_messaging/bin/loggingLoopApp',
        'easy_py_messaging/bin/loggingSpeedTest',
        'easy_py_messaging/bin/dirClient',
        'easy_py_messaging/bin/dirSvc',
        'easy_py_messaging/bin/client_create_class',
        'easy_py_messaging/bin/server_create_class',
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
setup(**setup_args)
