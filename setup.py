from setuptools import setup

install_requires = ['pyzmq', 'zmq']

setup_args = dict(
        name='rasppi_logger',
        version='0.1.0',
        description='A ZeroMQ based logger for distristributed Raspberry Pi systems',
        url='http://github.com/trailingdots/rasppi_logger',
        author='Cecil McGregor',
        author_email='TrailingDots@gmail.com',
        license='LGPL+BSD',
        packages='rasppi_logger',
        zip_safe=False,
        classifiers = [
            'Development Status :: 1 - Initial release',
            'Intended Audience :: Developers',
            'Intended Audience :: Intermediate software developers',
            'Intended Audience :: Systems Administrators',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'License :: OSI Approved :: CSD License',
            'Operating System :: Centos 7',
            'Operating System :: Debian',
            'Programming Language :: Python 2.7',
        ]
)

f 'setuptools' in sys.modules:
    setup_args['zip_safe'] = False
    pypy = 'PyPy' in sys.version
    if pypy:
        setup_args['install_requires'] = [
            'py',
        ]

setup(**setup_args)
