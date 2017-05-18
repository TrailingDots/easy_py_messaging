# The trivialApp Demo

This code provides a fast demonstration of the power of our
logging model.

Installing PyZMQ is a prerequesite.

cd to the directory in which easy_pi_messaging was installed.

To run this demo, open two terminals.

In one terminal, the `logCollector`, cd to the easy_pi_messaging/ directory.
The `logCollector.py` file should be present in this dir.

Now start the log collector:
```
    python logCollector.py --noisy
    logCollector: pid 23878, port 5570   # Startup message
    
```
A startup message of `logCollector: pid 23878, port 5570` 
confirms the logger will now accept logs from applications.
The pid of 23878 will almost certainly differ from invocation
to invocation.

In the other terminal, cd to examples/trivialApp.

In that window start sending some logs to the `logCollector`:
```bash
    python loggingApp.py 123
```
About once a second, output in the logCollector terminal
will appear as:
```
    INFO	ndx=1,host=metalic
    INFO	ndx=2,host=metalic
    INFO	ndx=3,host=metalic
    INFO	ndx=4,host=metalic
    ...
```

The "metalic" indicates the name of the computer the message
was sent. In this case, it is my desktop system. Your
output will differ.





