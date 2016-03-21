# The trivialApp Demo

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
A simple `Collector start` message confirms the logger can
accept logs from applications.

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
    Request #1 sent..
    Request #2 sent..
    ...
```

In the last window, start another instance of `loggingApp`:
```
    python loggingApp.py 456
```
And again, "456" provides a tag of the source of the log.

Notice the output on the `logCollector` terminal:
```
    ...
    Collector received "request #21" from "app-myApp-123"
    Collector received "request #1" from "app-myApp-456"
    Collector received "request #22" from "app-myApp-123"
    Collector received "request #2" from "app-myApp-456"
    ...
```
Your request numbers are likely different.

Notice the `logCollector` receives input logs from apps 123
and 456 at about once a second.

# Resilience in the Face of Crashes

These process can demonstrate resilience in the face of crashed
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
"crashed" suddenly appeared. These logs were buffered by the
loggingApp.

## Crashing Log Apps

A similar resilience exists in the senders of logs.
Automatic reconnection to the `logCollector` for new
log senders greatly simplifies system configurations.

Simulate a crashed log sender. In the `loggingApp 123`
terminal:
```
    Ctl-Z       # Throw the loggingApp into the background
    kill %1     # Kill the loggingApp
```
Notice the `logCollector` no longer lists "123" logs because the
"123" logging application has died.

The `logCollector` now has only "456" logs:
```
    Collector received "request #859" from "app-myApp-456"
    Collector received "request #860" from "app-myApp-456"
    Collector received "request #861" from "app-myApp-456"
    ...
```

Start the "123" log application again in the "123" terminal:
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
    ...
    Collector received "request #927" from "app-myApp-456"
    Collector received "request #1" from "app-myApp-123"
    Collector received "request #928" from "app-myApp-456"
    Collector received "request #2" from "app-myApp-123"
    Collector received "request #929" from "app-myApp-456"
    Collector received "request #3" from "app-myApp-123"
    ...
```

The "123" logging app has automatically reconnected! The "123" logging app
has also started countin from 1 because it has no memory of
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

## Potential Problems

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
another terminal. Multiple ways to fix this exist, only one is presented here.

To find and kill that other instance:
```
pstree -Alap >/tmp/tree.txt     # look at all processes in the system
vim /tmp/tree.txt               # Edit that file
/logCollector                   # Look for a logCollector process
```
More than one python program may be running. Continue searchig for a "python"
string similar to:
```
  |   |   |-python,21204 logCollector.py
  |   |   |   |-{python},21207
  |   |   |   |-{python},21208
  |   |   |   |-{python},21209
  |   |   |   `-{python},21210
```
The numbers are the pids (process ids) of tasks. The logCollector.py
code has multiple threads. Do not be concerned with these threads.
Just kill the main thread and the lower thread will die as well:
```
    kill -HUP 21204
```
Of course, use the pid from <i>your</i> display.

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


# Killing the Demonstation Processes

This version of the logCollector does not response to ^C to kill the
application.  Adding logic for this was deemed to only complicate the
demonstration.

Kill as:
```
    ^Z          # to put the app into the background.
    [1]+  Stopped                 python logCollector.py
    kill %1     # finally kills the process.
```
If the response to ^Z is "[2] ..." then use "kill %2", etc.



