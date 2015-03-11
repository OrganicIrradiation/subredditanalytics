import inspect
import logging

class logger(object):
    def __init__(self, name, level):
        """
        Initialize the class with some basic attributes.
        """

        self.level = level
        self.name = name
        self.setLogLevel(self.level)

    def setLogLevel(self,level):
        try:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)
        except:
            pass
        # create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level)
        # create console handler and set level to debug
        self.ch = logging.StreamHandler()
        self.ch.setLevel(level)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch
        self.ch.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(self.ch)

    def logDebug(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.debug("%s - %s" % (
            func.co_name,
            message
        ))
        
    def logInfo(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.info("%s - %s" % (
            func.co_name, 
            message
        ))
        
    def logWarn(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.warning("%s - %s" % (
            func.co_name,
            message
        ))
        
    def logError(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.error("%s - %s" % (
            func.co_name,
            message
        ))
        
    def logCrit(self, message):
        func = inspect.currentframe().f_back.f_code
        self.logger.critical("%s - %s in %s:%i" % (
            func.co_name,
            message,
            func.co_filename,
            func.co_firstlineno
        ))

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0
