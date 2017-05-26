# The trivialApp Demo

**** Doc the message format: separators, levels, ... ***

This code provides a fast demonstration of the power of our
logging model.

Installing PyZMQ is a prerequesite.

To run this demo, open three terminals. In each terminal
cd to the top level of the git repository.

In one terminal, the `logCollector`, cd to the lib/ directory.
Now start the log collector:
```
    python logCollector.py
```
A simple `logCollector: pid 1234` message confirms the logger can
accept logs from applications. The "1234" gets replaced by
the actual pid of the logCollector process. Note this pid
for later interactions.

In the other two terminals, cd to examples/trivialApp.

In one window start sending some logs to the `logCollector`:
```bash
    python loggingApp.py 123
```
The "123" provides an identification of the source of the logs.
In practice this "123" can be any string. For demonstration
purposes leave this as 123.

About once a second, output will start as:
```
    Request #1 "request #1"
    Request #2 "request #2"
    ...
```

In the last window, start another instance of `loggingApp`:
```
    python loggingApp.py 456
```
And again, "456" provides a tag of the source of the log.

By default the logCollector does not display received messages.
Change the mode of the logCollector to "noisy", meaning
incoming logs get echoed to the console of the logCollector.
In yet another console, send a USR1 signal to the logCollector:
```
    kill -USR1 1234
    ... Wait a few seconds and notice output on the logCollector console.
    kill -USR1 1234
```
Please do not be alarmed that linux uses a "kill" command
to send such signals. 

Notice the output on the `logCollector` terminal:
```
    Log tracing now ON
    request #13,host=worker-456
    request #418,host=worker-123
    request #14,host=worker-456
    request #419,host=worker-123
    request #15,host=worker-456
    Log tracing now OFF
```
Your request numbers are surely different.
Sending the USR1 signal toggles the noisy mode. 

Notice the `logCollector` receives input logs from apps 123
and 456 at about once a second.

# Resilience in the Face of Crashes

These process can demonstrate resilience in the face of crashed
processes.

## Crashing the logCollector

Demonstrate this by killing the `logCollector`:
```
    Ctl-C       # Kill the log collector.
```

Now start `logCollector` again in the `logCollector` terminal
and startup in noisy mode:
```
    python logCollector.py --noisy
    logCollector: pid 10056
    request #529,host=worker-123
    request #530,host=worker-123
    request #127,host=worker-456
    request #532,host=worker-123
    ... lots more
```
Did you notice a large amount of logs suddenly print on that
console? All those logs sent while the `logCollector` was
"crashed" suddenly appeared. These logs were buffered by the
loggingApp.

## Crashing Log Apps

A similar resilience exists in the senders of logs.
Automatic reconnection to the `logCollector` for new
log senders greatly simplifies system configurations.

Simulate a crashed log sender. In the `loggingApp 123`
terminal:
```
    Ctl-C       # Kill the logging App
```
Notice the `logCollector` no longer lists "123" logs because the
"123" logging application has died.

The `logCollector` now has only "456" logs:
```
    request #32,host=worker-456
    request #33,host=worker-456
    request #34,host=worker-456
    ...
```

Start the "123" log application again in the "123" terminal:
```
    python loggingApp.py 123
    >>> loggingApp: pid 10138
    loggingApp: Client worker-123 started
    Req #1 sent "request #1"
    Req #2 sent "request #2"
    ...
```

Now the logCollector has logs from "123" as well as "456":
```
    ...
    request #36,host=worker-123
    request #100,host=worker-456
    request #37,host=worker-123
    request #101,host=worker-456
    request #38,host=worker-123
    ...
```

The "123" logging app has automatically reconnected! The "123" logging app
has also started counting from 1 because it has no memory of
previous states.

This automatic reconnection from both sides provides an
incredible advantage to this library.

# What to Notice

Causing a crash of either logging app or logController does
prevent logging. But notice that restarting the crashed process
effortlessly reconnects! This provides an incredible benefit.
Struggling with connection problems has been a major pain
point of many developers.

Play with this example. Start yet another instance of the loggingApp
in another terminal and watch it start sending logs. Kill the
logCollector, wait awhile, then watch a restart list all those
buffered logs.

# Potential Problems

While playing with this demo, perhaps a message appears that causes problems:
```
    python logCollector.py
    >>> logCollector: pid 10994
    ZMQError:Address already in use
    Please kill other instances of this program.
    Or: another program may be using port tcp://*:5570
    Exiting
    ....
```
Most likely another instance of logCollector.py runs in the background or on
another terminal. Multiple fixes can apply, only one is presented here.

This message may happen if you play with the code. Most certainly playing
with code <i>is</i> encouraged!

To find and kill that other instance:
```
    ps a | grep logCollector
    12919 pts/4    Sl+    0:00 python logCollector.py
    12930 pts/0    S+     0:00 grep --color=auto logCollector
```
Another way:
```
    pstree -Alap | grep logCollector  
      |   |   `-python,12919 logCollector.py
      |   |   |-grep,10787 --color=auto logCollector
```
Ignore the lines with "grep". The pid of logCollector is 12919.
The numbers are the pids (process ids) of tasks. kill the logCollector:
```
    kill -INT 12919
```
Of course, you must use the pid from <i>your</i> display.

# A Speed Test

How many messages can your system manage? This actually depends
upon multiple factors:

* How large are your messages? The larger the messages, the longer
the time it takes to generate, send and process.

* How is the message configured? The fastest method would have
both the messaging app and the logCollector on the same system.
The slowest would have the app and logCollector on different
systems communicating by wireles. An intermediate speed would
use an ethernet cable between the two systems.

* The more complex the message, the more processing.

* If this gets run between different systems, the communications
hardware has a huge impact. Ethernet cables provide speedy
delivery, wifi the slowest. Any messaging overhead gets
swamped by these messenger carriers.

## Running The RaspPiLogger Speed "Benchmark"

A simple speed test has been included. The developer must make minor
modifications to run the speed tests depending on configurations. The changes
represent the identical changes used to setup a remote system.

Start with the default system. This connects both app and logCollector
on the same system. The app and logCollector live as separate
processes with the app sending simple log messages to the logCollector.

Open two terminals and cd to the lib directory: "loggerZeroMQ/lib".

In one terminal remove old log files and start the logCollector:
```
    rm logs.log     # Remove any previous log file, if any.
    python logCollector.py 
    logCollector: pid 13701
```
The logCollector.py will not echo incoming logs. However, if it were to echo,
the speed could <i>not</i> slow because the sender of the logs does
not wait for a reply. With a noisy logCollector, outputting to the
console takes time. On my system a noisy logColector does not
impact overall speed of the senders.

In the other terminal, start the process that sends 100,000 messages:
```
    python loggingSpeedTest.py 
    >>> loggingSpeedTest: pid 14823
    100000 logs, elapsed time: 1.443560
    69273 messages per seond
    loggingSpeedTest
```
A speed of over 69,000 messages/sec will should adequately fulfill
most requirements! Since this project targets Raspberry Pi and Arduino
like systems, this speed should work well for the vast majority
of projects. However, building clusters of these boards could
suggest a rewrite in C++ or C.

Run any benchmark multiple times and take the average. Running
and averaging five times on my systems resulted in a average
of 72,834 messages/sec.

On a Raspberry Pi system sending logs to my linux desktop,
this speed test reported 100,000 logs in
12.17 seconds. 8,217 messages/second should provide adequate
message throughput for your Raspberry Pi system.

# Connecting Raspberry Pi to Desktop System

The intent of this project connects a Raspberry Pi to
other Raspberry Pi systems and/or a desktop system.
The system may consist of Raspberry Pis only, or
a connected desktop system functioning as a central
repository of logs.

The simpler configuration of a Raspberry Pi to a desktop proceeds
as follows.
<p><br><center><img src="./images/RaspPiToDesktop.png"></center><br/></p>

Begin by installing the repository on both the desktop and Raspberry Pi system.
Refer to the installation instructions above if necessary.

On the desktop system, find the ip address:
```bash
hostname -I
192.168.1.116 ...      # Use the first ip address 
export RASPI=192.168.1.116
```
Your system may require another command. If necessary goggle "ip address debian".

This process sets the IP address of your Raspberry Pi to the $BASH
environmental variable.

Validate your IP address by pinging:
```
    ping 192.168.1.116      # My desktop ping
    PING 192.168.1.116 (192.168.1.116) 56(84) bytes of data.
    64 bytes from 192.168.1.116: icmp_seq=1 ttl=64 time=0.062 ms
    64 bytes from 192.168.1.116: icmp_seq=2 ttl=64 time=0.060 ms
```

On your Raspberry Pi system, set and environmental variable to the IP address
of the desktop system:
```
export DESKTOP=192.168.1.116
```
To ensure communications "ping" the desktop from the Raspberry Pi system.
In a Respberry Pi terminal:
```
ping $DESKTOP
PING 192.168.1.116 (192.168.1.116) 56(84) bytes of data
64 bytes from 192.168.1.116: icmp_req=1 time=2.60ms
64 bytes from 192.168.1.116: icmp_req=1 time=15.3ms
...
```
Your output should result in a similar, but not identical response.
The ensure the desktop and Raspberry Pi systems can talk to each other.

## Netcat to Simulate Messaging

Beginning with a simple standard TCP/IP tool, netcat, we must
ensure the network can properly transfer messages between our
two systems. Netcat has been chosen because its use provides
a level of confidence.

Simulate sending a message from the Raspberry Pi to the desktop.
Many systems have various firewalls and other security features to
prevent message exchanges. Unfortunately I cannot cover all possible
combinations because your system may not display the same behavior.

Use netcat, a useful TCP/IP Swiss Army knife.
If necessary, install it from 
<a href="https://nmap.org/ncat/">https://nmap.org/ncat/</a> .

Netcat has a linux name of 'nc' and may already exist on your computer.

On the desktop system, start listening to a port:
```
nc -l 5570          # Listen to everything on port 5570
```
Port 5570 is the standard port used by ZeroMQ.

If the following netcat tests do not work, certainly the
logging will not work.

On your Raspberry Pi, start sending message using netcat:
```
nc $DESKTOP 5570
Hello world!
A message from a Raspberry Pi to the desktop.
```
If everything works well, the "Helo world!" and "A message..." should
appear on your desktop.

Enter other messages and notice they get sent and echoed on the desktop.

If all does not go well, the output starts as:
```
nc $DESKTOP 5570
```
And the responses could vary. The first indicator of trouble is the
lack of output on the desktop.

On the Raspberry Pi executing nc could simply drop back to the command prompt.
Or the netcat prompt accepts messages but nothing appears on the desktop. 
Or the connection may be refused.

Unfortunately in these cases possible solutions are too long to properly handle
in this document. Please google "netcat testing network systems debugging".

## Messages Between a Raspberry Pi and the Desktop

Now that we know message pass cleanly between our two systems,
we can now send logs.

On the desktop system, in the lib directory, start the logCollector:
```
    python logCollector.py
    >>> logCollector.py: pid 23301
    Worker started
```
Logs received on the desktop get stored in  the ./lib/logs.log file.

On the Raspberry Pi in the lib directory, start sending some logs:
```
    python loggingApp.py 777
    >>> loggingApp: pid 3120
    loggingApp: Client worker-777 started

    Req #1 sent
    Req #2 sent
    ...
```
The loggingApp send message once a second to the desktop. 

# The Python Code: LogCollector.py

This code demonstrates a modified [Asynchronous Client/Server Pattern](http://zeromq.org/intro:read-the-manual). 
The original code from the ZeroMQ library handled bidirectional messages. For
purposes of logging, only one direction was required.

## logCollector.py

This code implements a LogCollectorTask
that initialized ZeroMQ and starts the collector.

The `run` method in the `ServerCollector` class receives
messages and simply prints them. 

if desired, a user could change the print to saving to a
file and use this code as a  log collector.

The existing LogCollectorTask writes the input messages to a log
file. Each log entry gets a timestamp prepended to the log.

A message consists of the following fields:

    Timestamp: The format is [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601),
    a common representation. The timezone, however, is in <i>local</i>
    time rather than the ISO 8601 UTC standard time. This time zone was
    chosen because we generally use our SOC systems around the house
    and do not need to deal with time conversions.

    A tab, '\t': A tab separates the three fields.

    Log level: One of DEBUG, INFO, WARNING, ERROR or CRITICAL.

    A tab.

    The payload. The message supplied by the log sender. This may be
    any string. To provide decent logging, a uniform logging convention
    must apply to these logs. Specifcially this means each application
    using logCollector should have the same formats for logs. See below
    for a discussion on this.

    End of line. Since this runs on linux, the standard '\n' applies.

## Payloads

Using keyword=value provides great flexibility in constructing logs.
The keyword=value significantly eases parsing of these logs
by analytic code used to filter and interpret logs.

Follow-on code for analytics ...


## loggingApp.py

This code requires a single command line argument to
operate and send logs. The last two lines in the file
create a logging application and start sending logs.

The relevant lines that perform sending logs:
``` python
    socket.send_string(u'request #%d' % (reqs))
    print('Request #%d sent..' % (reqs))
    time.sleep(1)   # Slow the log stream down!
```
The `socket.send_string()` send the formatted string
to the `logCollector`. 

A real logging application would provide more meaningful
messages.

The `sleep(1)` slows the logs down to once per second.
Comment out this line and notice how fast logs get
printed from `logCollector`!

On my system I have sent 100,000 logs in 1.3 seconds.
This is likely fast enough for most applications!

