import datetime


class Logmanager(object):
    defaultThreshold = 2
    defaultFile = "main.log"
    defaultLogToConsole = False

    def __init__(self):
        self.threshold = self.defaultThreshold
        self.file = self.defaultFile
        self.logToConsole = self.defaultLogToConsole
        self.backlog = []

    def backlogAppend(self, level, message):
        self.backlog.append([level, message])

    def backlogFlush(self):
        for log in self.backlog:
            self.log(log[0], log[1])

    @staticmethod
    def formatter(message):
        print('formatter')
        return str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]\t" + message))

    def log(self, level, message):
        if self.threshold >= level and self.threshold != 0:
            if self.logToConsole:
                print(self.formatter(message))
            else:
                print('logging to file')
                file = open(self.file, "a")
                file.write(self.formatter(message) + "\n")
                file.close()




def initConfig():
    logger.backlog.append([3, "Function initConfig was called"])
    infile = open('.\\config.ini', 'r')
    lines = infile.read().split('\n')
    options = dict()
    for line in lines:
        if (line == ''):
            continue
        if (line[0] == '[') | (line[0] == '#'):
            continue
        if line.split(': ') == 1:
            key, option = line.split(':')
        else:
            key, option = line.split(': ')
        options[key] = option

    initLoggingThreshold(options)
    initLogFile(options)
    initLogConsole(options)


def initLoggingThreshold(options):
    loggingSwitcher = {
        'NONE': 0,
        'ERROR': 1,
        'WARN': 2,
        'INFO': 3,
        'LOG': 4,
        'DEBUG': 5
    }

    if 'Logging threshold' in options.keys():
        if options['Logging threshold'] in loggingSwitcher.keys():
            logger.backlogAppend(4, 'A valid option for logging threshold was found in the configfile!')
            logger.threshold = loggingSwitcher.get(options['Logging threshold'])
        else:
            logger.threshold = 2
            logger.backlogAppend(2, "No valid option for logging threshold was found in the config file!")
            logger.backlogAppend(2, "Defaulting to level 2, errors amd warnings only!")
    else:
        logger.threshold = 2
        logger.backlogAppend(2, "Logging threshold was not defined in the config file!")
        logger.backlogAppend(2, "Defaulting to level 2, errors amd warnings only!")
    logger.backlogAppend(5, "loggingThreshold set to: " + str(logger.threshold))


def initLogConsole(options):
    if 'Logging target' in options.keys():
        if options['Logging target'].upper() == 'CONSOLE':
            logger.backlogAppend(4, 'A valid option for logging target was found in the config file!')
            logger.logToConsole = True
        elif options['Logging target'].upper() == 'FILE':
            logger.backlogAppend(4, 'A valid option for logging target was found in the config file!')
            logger.logToConsole = False
        else:
            logger.backlogAppend(2, "No valid option for logging target was found in the config file!")
            logger.backlogAppend(2, "Defaulting to FILE")
            logger.logToConsole = False
    logger.backlogAppend(5, "logConsole set to: " + str(logger.logToConsole))


def initLogFile(options):
    global logFile
    if 'Log file' in options.keys():
        if 'Log file' in options.keys():
            logger.backlogAppend(4, 'A valid option for log file was found in the configfile!')
            logFile = options['Log file']
        else:
            logFile = ".\\main.log"
            logger.backlogAppend(2, "No valid option for log file was found in the config file!")
            logger.backlogAppend(2, "Defaulting to .\\main.log!")
    logger.backlogAppend(5, "logFile set to: " + str(logFile))




logger = Logmanager()
logger.backlogAppend(1, "###### VSFTPD log Analyzer started ######")

initConfig()
logger.backlogFlush()