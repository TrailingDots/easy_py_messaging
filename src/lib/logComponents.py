"""
    Class to handle logging of components on the
    remote side.
"""
import logging
import utils


class LogComponents(object):
    """
    Clients can use this to construct individual components
    of a log message.
    """
    def __init__(self, level='INFO', payload=''):
        self.level = level
        if self.level not in utils.LOG_LEVELS:
            # Assume an invalid level is a DEBUG
            self.level = logging.DEBUG
        self.payload = payload
        self.items = {
                'level': self.level,
                'payload': self.payload
        }

    @staticmethod
    def msg_to_components(msg):
        """
        Static method!

        Given a separated message, return a class instance with components.

        If components do not exist in the msg, defaults get used.
        'DEBUG' = the default log level.
        ''      = default payload.

        Return with an instance of this class with proper components.
        """
        msg_list = msg.split(utils.SEPARATION_CHAR)
        if len(msg_list) < 2:
            # On missing parts of a message, assume an invalid
            # log contains debug messages.
            msg_list.insert(0, 'DEBUG')
        logLevel = msg_list[0].upper()
        if logLevel not in utils.LOG_LEVELS:
            # This will not fail if msg_list is empty.
            # Default to debug level
            logLevel = 'DEBUG'
        return LogComponents(level=logLevel, payload=msg_list[1])

    def __str__(self):
        """
        Create a string formatted for sending to the
        log collector.
        """
        msg = self.level + utils.SEPARATION_CHAR + \
              self.payload
        return msg

