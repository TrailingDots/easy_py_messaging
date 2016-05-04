"""
    A setuptools based setup module.
"""
# Prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

project = 'simple_log_messaging'

"""
    entry_points={
        'console_scripts': [
            'logCollector=simple_log_messaging.logCollector:main',
            'logCmd=simple_log_messaging.logCmd:main',
            'listeningPort=simple_log_messaging.listeningPort:main',
            'logFilterApp=simple_log_messaging.logFilterApp:main',
        ]
    },
"""
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
            'simple_log_messaging/bin/logCollector',
            'simple_log_messaging/bin/logCmd',
            'simple_log_messaging/bin/listeningPort',
            'simple_log_messaging/bin/logFilterApp',
            'simple_log_messaging/bin/loggingLoopApp',
            'simple_log_messaging/bin/loggingSpeedTest',
            'simple_log_messaging/bin/dirClient',
            'simple_log_messaging/bin/dirSvc',
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
