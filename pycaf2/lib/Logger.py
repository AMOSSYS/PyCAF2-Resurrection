# -*- coding: utf-8 -*-
# Logger inspired from the Hooker project: https://github.com/AndroidHooker/hooker

from logging import StreamHandler, FileHandler, DEBUG, INFO, getLogger as realGetLogger, Formatter

try:
    from colorama import Fore, Back, Style

    class ColourStreamHandler(StreamHandler):
        """ A colorized output SteamHandler """

        # Some basic colour scheme defaults
        colours = {
            'DEBUG' : Fore.CYAN,
            'INFO' : Fore.GREEN,
            'WARN' : Fore.YELLOW,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRIT' : Back.RED + Fore.WHITE,
            'CRITICAL' : Back.RED + Fore.WHITE
        }

        @property
        def is_tty(self):
            """ Check if we are using a "real" TTY. If we are not using a TTY it means that
            the colour output should be disabled.

            :return: Using a TTY status
            :rtype: bool
            """
            try: return getattr(self.stream, 'isatty', None)()
            except: return False

        def emit(self, record):
            try:
                message = self.format(record)

                if not self.is_tty:
                    self.stream.write(message)
                else:
                    self.stream.write(self.colours[record.levelname] + message + Style.RESET_ALL)
                self.stream.write(getattr(self, 'terminator', '\n'))
                self.flush()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    has_colour = True
except Exception as e:
    print("ERRROR: {}".format(e))
    has_colour = False

def getLogger(name=None, fmt='[%(processName)s/%(filename)s:%(lineno)s/%(levelname)s] %(relativeCreated)d: %(message)s'):
    """ Get and initialize a colourised logging instance if the system supports
    it as defined by the log.has_colour

    :param name: Name of the logger
    :type name: str
    :param fmt: Message format to use
    :type fmt: str
    :return: Logger instance
    :rtype: Logger
    """

    log = realGetLogger(name)
    if not len(log.handlers):
        # Enable colour within handlerConsole if support was loaded properly
        consoleHandler = ColourStreamHandler() if has_colour else StreamHandler()
        consoleHandler.setLevel(DEBUG)
        consoleHandler.setFormatter(Formatter(fmt))

        log.addHandler(consoleHandler)

        # @TODO: put this in main so we can specify the log file
        fileHandler = FileHandler(filename="output.log")
        fileHandler.setLevel(INFO)
        fileHandler.setFormatter(Formatter(fmt='%(message)s'))
        log.addHandler(fileHandler)

        log.setLevel(DEBUG)
        log.propagate = False
    return log
