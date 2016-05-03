#
# Configuration file for accumulating logs
#
import platform
import os

# Set to a filename to log messages.
# Leaving this set to None will output
# logs to stdout.
LOG_FILENAME = None

#
# Log level setting: Only logs of this level
# and above get logged.
#
#    The default logging level is logConfig.LOG_LEVEL. To log everything,
#    change the level at any time:
#        logger.basicConfig(level=logging.NOTSET)
#
#    Set level to warning and above:
#        logger.basicConfig(level=logging.WARNING)
#
#    Set level to debug and above for development:
#        logger.basicConfig(level=logging.WARNING)
#
LOG_LEVEL = 'WARNING'

#
# -------------------------------
# CHANGE TO THE IP OF SERVER!
# -------------------------------
DEFAULT_SERVER = '127.0.0.1'  # YOUR logging server name or IP

# Echo incoming messages to the console.
# Turn on with the -n commandline option.
NOISY = False

# ==============================================
# ==============================================
# ****    Change NOTHING below this line!   ****
# ==============================================
# ==============================================
SCHEME = 'tcp'
COLL_HOST = '*'         # Only the server collector uses this.
# Logging Port
PORT = 5570             # Do NOT change!
def get_logging_port():
    return PORT

# Directory Service Port
DIR_PORT = PORT + 1
def get_directory_port():
    return get_logging_port() + 1


# Testing code needs to use this
# All testing is performed on localhost.
# Later:
# Perform testing on remotes and/or a cluster.
TESTING = os.getenv('TESTING')

if platform.node() == DEFAULT_SERVER or TESTING:
    APP_HOST = 'localhost'     # For testing on the log server
else:
    APP_HOST = DEFAULT_SERVER

# Connect socket string
# Likely to change only the HOST and PORT
# See: https://en.wikipedia.org/wiki/Uniform_Resource_Locator#Syntax
# The socket name the applications should use.
# The application should use this for the socket.
APP_SOCKET = '%s://%s:%d' % (SCHEME, APP_HOST, PORT)

COLL_SOCKET = '%s://%s:%d' % (SCHEME, COLL_HOST, PORT)

