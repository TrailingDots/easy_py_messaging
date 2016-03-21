# 

[![Build Status](https://travis-ci.org/zeromq/libzmq.png?branch=master)](https://travis-ci.org/zeromq/libzmq)
[![Build status](https://ci.appveyor.com/api/projects/status/e2ks424yrs1un3wt?svg=true)](https://ci.appveyor.com/project/zeromq/libzmq)

## Welcome

The Raspberry Pi lightweight logger is a library which implements
a ZeroMQ based messaging to privde logging facilities for
distributed systems. This robust library extends the ZeroMQ messaging
system to allow easy interfaces to distributed systems.
While specifically developed for distributed Raspberry Pi
systems, it is easily installed in almost any linux system.

This code contains a logcollector to receive and store logs,
a log filter application to read and filter logs based on
multiple configurable criteria.

The library contains an easy-to-use python class for interfacing
with the lower level ZeroMQ messaging system. Now sending
log messages eases the problems associated with monitoring and
debugging problems with distributed systems.


## Building and installation

See the INSTALL file included with the distribution.

## Resources

Extensive documentation is provided with the distribution. Refer to
docs/RaspPiLOgger.html.

Git repository: http://github.com/trailingdots/rasppilogger

## License

The project license is specified in COPYING and COPYING.LESSER.

rasppilogger is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License (LGPL) as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

As a special exception, the Contributors give you permission to link
this library with independent modules to produce an executable,
regardless of the license terms of these independent modules, and to
copy and distribute the resulting executable under terms of your choice,
provided that you also meet, for each linked independent module, the
terms and conditions of the license of that module. An independent
module is a module which is not derived from or based on this library.
If you modify this library, you must extend this exception to your
version of the library.

rasppilogger is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
License for more details.
