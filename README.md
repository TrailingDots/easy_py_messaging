
# DRAFT ONLY - This code is under heavy development. PLEASE do not use!!


# easy_log_messaging - version 1.0.0
A simple to use wrapper around ZeroMQ for distributed systems to use for logging.

## Welcome

The Simple Log Messaging is a lightweight logger is a library which implements
a ZeroMQ based messaging to privde logging facilities for distributed systems.
This robust library extends the ZeroMQ messaging system to allow easy
interfaces to distributed systems.  While specifically developed for
distributed Raspberry Pi and similar systems, it is easily installed in almost
any linux system. Additionaly, this code seamlessly when all processes
exist on the same node.

This code contains a log collector to receive and store logs,
a log filter application to receive, store and filter logs.

The library contains easy-to-use python classes for interfacing with the lower
level ZeroMQ messaging system. Users will enjoy the simplicity of interfacing
these classes with their own applications. Now sending log messages eases the
problems associated with monitoring and debugging problems with distributed
systems.


## Building and installation

See the [INSTALL](./easy_log_messaging/docs/easy_log_messaging.html)
file included with the distribution.

## Resources

Extensive documentation is provided with the distribution. Refer to
[Simple Log Messaging](./easy_log_messaging/docs/easy_log_messaging.html).

Git repository: [Simple Log Messaging](http://github.com/trailingdots/easy_log_messaging).

## License

The project license is specified in COPYING and COPYING.LESSER.

Simple Log Messaging is free software; you can redistribute it and/or modify it
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

Simple Log Messaging is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
more details.

