easy\_py\_messaging - version 1.2.0
=================================

easy\_py\_messaging is a simple to use python wrapper around ZeroMQ for distributed 
systems to use for messaging. For illustration purposes, a non-trivial logging application
is presented. 

This package runs on most linux systems: Centos, Ubunty, Debian,
Raspberry Py and like most other linux offerings. It does not run
on Windows.

A logging application demonstrates the power of ZeroMQ and the
implemented wrapper. This serves to use ZeroMQ in a non-trivial
manners and to show how flexible python can be in messaging 
applications.

## Welcome

The Easy Py Messaging system provides lightweight messaging in a library
which implements a ZeroMQ based messaging to privde logging facilities for
distributed systems.  This robust library uses the excellent ZeroMQ messaging
system to allow easy interfacing with distributed systems.  While
specifically developed for distributed Raspberry Pis and similar systems, it
is easily installed in almost any Linux system. Additionaly, this code works
seamlessly when all processes exist on the same node.

This code contains a synchronous messaging API, a log collector to receive
and store logs, a log filter application to receive, store and filter logs.
Additional support utilities enhance and support this product.

The library contains easy-to-use python classes for interfacing with the lower
level ZeroMQ messaging system. Users will enjoy the simplicity of interfacing
these classes with their own applications. 

The logging system can easily collect logs from remote systems and store
them. Now consolidated log messages eases the problems associated with
monitoring and debugging problems with distributed systems.


## Building and installation

Installation consists of the normal:
``` bash
git clone https://github.com/TrailingDots/easy_py_messaging.git
python setup.py install
```
"sudo" may or may not be required depending upon your particular
system configuration.

### Dependencies

Your system may or may not require additional dependencies.

#### ZeroMQ

The backbone of this offering uses [ZeroMQ](http://zeromq.org/) for
low level, fast message handling.

Install ZeroMQ from the above site. The instructions are straightforward
and should present no problems.

#### Python pip and setup tools
You might need these tools. Most python developers have these
already installed. See <a href="https://packaging.python.org/install\_requirements\_linux/">Installing pip/setuptools/wheel with Linux Package Managers</a>.
Windows and OSX are on sister pages.

#### Developer tools
If you choose to develop with code from this package, the
runTests.sh script includes a somewhat exhaustive suite
of testing that includes timing, unit tests and clean code
checking.

This project has been careful to provide clean code as determined
by pyflakes, unit test, python lint, etc.

To eliminate the static checkers, examing the section
executing pyflakes, lizard, pep8, etc. and comment out
these lines.

#### Pyflakes - The passive checker of Python programs

Pyflakes is a code analysis tool for Python. Pyflakes
does not execute code, but rather analyzes the code.
See <a href="https://launchpad.net/pyflakes">pyflakes</a> or this
<a href="https://www.blog.pythonlibrary.org/2012/06/13/pyflakes-the-passive-checker-of-python-programs/">pyflakes</a> and follow the
installation instructions.

#### Lizard - for cyclomatic complexity

Cyclomatic complexity determines the complexity of Python
code. Reducing the complexity allows code to usually be
more readable, testable and maintainable.

This may be ignored by commenting out the lizard
command in runTests.sh.

To install lizard, see <a href="https://github.com/terryyin/lizard">lizard</a>.

#### pep8 - Style Guile for Python Coding

pep8 checks Python code against the recommended style conventions.
See <a href="https://pypi.python.org/pypi/pep8">pep8 - Python style guide checker</a>.

If desired, comment out the line in runTest.sh to ignore this.

#### Python bindings for ZeroMQ

The Python bindings for Zero MQ are <b>required</b> since the
intent of the package drives an easy Zero MQ interface.


## Documentation and Utilities

The distribution provides extensive documentation. Refer to
[Easy Py Messaging](./easy_py_messaging/docs/easy_py_messaging.html).
Developers should start here.


## Tutorial
A tutorial: [Easy Py Messaging Tutorial](./easy_py_messaging/docs/easyMessagingTutorial.html).

This tutorial presents minimal logic for client and server code as well
as tourbleshooting guidelines.

## Details: The Log Collection Application

[Easy Log Collection by Messaging](./easy_py_messaging/docs/logCollector.html) represents
a significant application using the messaging concepts implemented for
this package. A log collector repsents a utility that most applications
could use. Logging has been underrated in every site I have worked.
Yet logging remains the primary debugging source of live systems.
Without proper logging, knowledge of your working system will
remain elusive and mysterious.

## License

The project license is specified in COPYING and COPYING.LESSER.

Easy Py Messaging is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License (LGPL) as published by
the Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

As a special exception, the Contributors give you permission to link
this library with independent modules to produce an executable,
regardless of the license terms of these independent modules, and to
copy and distribute the resulting executable under terms of your choice,
provided that you also meet, for each linked independent module, the
terms and conditions of the license of that module. An independent
module is a module which is not derived from or based on this library.
If you modify this library, you must extend this exception to your
version of the library.

Easy Py Messaging is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
more details.

