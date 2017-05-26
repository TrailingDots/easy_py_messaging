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
    version='2.0.2',
    description='A python-based ZeroMQ based logging system for distributedsystems',
    author='Trailing Dots',
    keywords='ZeroMQ 0mq distributed networking messaging socket client server p2p publish subscribe requrest reply push pull backend microservices python',
    author_email='TrailingDots@gmail.com',
    license='LGPL',
    install_requires=['pyzmq'],
    zip_safe=False,
    packages=[project],
    include_package_data=True,
    scripts = ["easy_py_messaging/logCollector.py",
        "easy_py_messaging/server_create_basic.py",
        "easy_py_messaging/client_create_class.py",
        "easy_py_messaging/logFilter.py",
        "easy_py_messaging/utils.py",
        "easy_py_messaging/server_create_class.py",
        "easy_py_messaging/.logcollectorrc",
        "easy_py_messaging/demoSocket.py",
        "easy_py_messaging/dirSvc.py",
        "easy_py_messaging/logCmd.py",
        "easy_py_messaging/logFilterApp.py",
        "easy_py_messaging/loggingSpeedTest.py",
        "easy_py_messaging/server_create_test.py",
        "easy_py_messaging/client_create_nano.py",
        "easy_py_messaging/logComponents.py",
        "easy_py_messaging/server_create_nano.py",
        "easy_py_messaging/client_create_basic.py",
        "easy_py_messaging/client_create_skeleton.py",
        "easy_py_messaging/client_create_test.py",
        "easy_py_messaging/client_sync.py",
        "easy_py_messaging/dirClient.py",
        "easy_py_messaging/loggingClientTask.py",
        "easy_py_messaging/apiLoggerInit.py",
        "easy_py_messaging/logConfig.py",
        "easy_py_messaging/loggingLoopApp.py",],
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

