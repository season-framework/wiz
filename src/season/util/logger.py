import time

class Logger:
    LOG_DEBUG = 0
    LOG_INFO = 1
    LOG_WARN = LOG_WARNING = 2
    LOG_DEV = 3
    LOG_ERR = LOG_ERROR = 4
    LOG_CRIT = LOG_CRITICAL = 5

    def __init__(self, *tags, level=LOG_DEV, trigger=None):
        self.trigger = trigger
        self.level = level
        self.tags = tags

    def __call__(self, *args, level=LOG_DEV):
        if level < self.level: return
        tag = ""
        if len(self.tags) > 0:
            tag = "[" + "][".join(self.tags) + "]"
    
        tagmap = ['DEBUG', 'INFO_', 'WARN_', 'DEV__', 'ERROR', 'CRIT_']
        tagcolor = [94, 94, 93, 94, 91, 91]
        if level < len(tagmap): tag = "[" + tagmap[level] + "]" + tag
        color = tagcolor[level]

        args = list(args)
        for i in range(len(args)): 
            args[i] = str(args[i])
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        logdata = f"\033[{color}m[{timestamp}]{tag}\033[0m " + " ".join(args)

        if self.trigger is not None:
            self.trigger(logdata)
    
    def debug(self, *args):
        self(*args, level=self.LOG_DEBUG)
    
    def info(self, *args):
        self(*args, level=self.LOG_INFO)
    
    def warn(self, *args):
        self(*args, level=self.LOG_WARN)
    
    def warning(self, *args):
        self(*args, level=self.LOG_WARN)

    def dev(self, *args):
        self(*args, level=self.LOG_DEV)
    
    def err(self, *args):
        self(*args, level=self.LOG_ERROR)

    def error(self, *args):
        self(*args, level=self.LOG_ERROR)
    
    def crit(self, *args):
        self(*args, level=self.LOG_CRITICAL)
    
    def critical(self, *args):
        self(*args, level=self.LOG_ERROR)
    