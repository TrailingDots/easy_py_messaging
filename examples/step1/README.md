# The step1 Demo App

This code provides a fast demonstration of the power of our
logging model.

Installing PyZMQ is a prerequesite.

To run this demo, open three terminals.

In each terminal cd to the step1 directory on your machine.

In one terminal, the `logCollector`, start the log collector:
```
    python logCollector.py
```
A simple `Collector start` message confirms the logger can
accept logs from applications.

In the second window start sending some logs to the `logCollector`:
```
    python loggingApp.py 123
```
The "123" provides an identification of the source of the logs.

At about once a second, output will start as:
```
    Request #1 sent..
    Request #2 sent..
    ...
```

In the third window, start another instance of `loggingApp`:
```
    python loggingApp.py 456
```
And again, "456" provides a tag of the source of the log.

Notice the output on the `logCollector` terminal:
```
    Collector received "request #21" from "app-myApp-123"
    Collector received "request #1" from "app-myApp-456"
    Collector received "request #22" from "app-myApp-123"
    Collector received "request #2" from "app-myApp-456"
```
Your request numbers are likely different.

Notice the `logCollector` receives input logs from apps 123
and 456 at about once a second.

```

         +---------+        +---------+
         |Client 1 |        |Client 2 |
         |(Dealer) |        |(Dealer) |
         +---------+        +---------+
              |                  |
              V                  V
              +------------------+
                       |
                       V
                +--------------+
                | LogCollector |
                |   (Router)   |---> file, database, etc.
                +--------------+

```
The notational "Dealer" and "Router" refer to the
ZeroMQ patterns used by this code.

# Resilience in the Face of Crashes

These processes can demonstrate resilience in the face of crashed
processes.

## Crashing the logCollector

Demonstrate this by killing the `logCollector`:
```
    Ctl-Z       # Throw the logCollector into the background.
    kill %1     # Kill that background process
```

Now start `logCollector` again in the `logCollector` terminal:
```
    python logCollector.py
    Collector started
    Collector received "request #299" from "app-myApp-123"
    Collector received "request #279" from "app-myApp-456"
    Collector received "request #300" from "app-myApp-123"
    Collector received "request #280" from "app-myApp-456"
    ... lots more
```
Did you notice a large amount of logs suddenly print on that
console? All those logs sent while the `logCollector` was
"crashed" suddenly appeared.

## Crashing Log Apps

A similar resilence exists in the senders of logs.
Automatic reconnection to the `logCollector` for new
log senders greatly simplifies system configurations.

Simulate a crashed log sender. In the `loggingApp 123`
terminal:
```
    Ctl-Z       # Throw the loggingApp into the background
    kill %1     # Kill the loggingApp
```
Notice the `logCollector` has no "123" logs because the
sender has died.

The `logCollector` now has only "456" logs:
```
    Collector received "request #859" from "app-myApp-456"
    Collector received "request #860" from "app-myApp-456"
    Collector received "request #861" from "app-myApp-456"
    ...
```

Start the "123" log send again:
```
    python loggingApp.py 123
    ApplicationTask app-myApp-123 started
    Request #1 sent..
    Request #2 sent..
    Request #3 sent..
    ...
```

Now the logCollector has logs from "123" as well as "456":
```
    Collector received "request #927" from "app-myApp-456"
    Collector received "request #1" from "app-myApp-123"
    Collector received "request #928" from "app-myApp-456"
    Collector received "request #2" from "app-myApp-123"
    Collector received "request #929" from "app-myApp-456"
    Collector received "request #3" from "app-myApp-123"
    ...
```

The "123" logging app has automatically reconnected!

This automatic reconnection from both sides provides an
incredible advantage to this library.

# The Python Code

This code demonstrates a modified [Asynchronous Client/Server Pattern](http://zeromq.org/intro:read-the-manual). 
The original code handled bidirectional messages. For purposes of
logging, only one direction was required.

This code deliberately exposes some "plumbing" that will be
hidden in future code. Please do not let this put you off.

## logCollector.py

This code consists of two classes:
    * ServerTask: Initialized ZeroMQ and start the collector.

    * ServerCollector: Collect logs from applications and
    print the log.

The `run` method in the `ServerCollector` class receives
messages and simply prints them. 

if desired, a user could change the print to saving to a
file and use this code as a  log collector.

## loggingApp.py

This code requires a single command line argument to
operate and send logs. The last two lines in the file
create a logging application and start sending logs.

The relevant lines that perform sending logs:
```
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

On my system I have send 100,000 logs in 1.3 seconds.
This is likely fast enough for most applications!
Since this suite of applications is targeted to
members of the Maker Movement, this should provide
a very fast messaging service for all but the most
demanding applications.


## Killing the Demonstation Processes

This version does responds to ^C to kill the application.



