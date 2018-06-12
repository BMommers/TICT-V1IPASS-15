import datetime, tkinter, sys, tkinter.filedialog, tkinter.messagebox


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
        return str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]\t" + message))

    def log(self, level, message):
        if self.threshold >= level and self.threshold != 0:
            if self.logToConsole:
                print(self.formatter(message))
            else:
                file = open(self.file, "a")
                file.write(self.formatter(message) + "\n")
                file.close()


def analyseLogfile():
    fileObject = open(logFile, 'r')
    for line in fileObject:
        Line(line)


class Line:
    def __init__(self, line):
        data = line.split(" ")
        print(data)


class Client:
    allClients = []

    def __init__(self, ip):
        self.ip = ip
        self.logInAttempts = 1
        Client.allClients.append(self)

    def loggedIn(self):
        self.logInAttempts =+ 1


class File:
    allFiles = []

    def __init__(self, filename, found):
        File.allFiles.append(self)
        self.name = filename
        self.found = found
        self.count = 0

    def downloaded(self):
        self.count += 1


def initConfig():
    logger.backlog.append([3, "Function initConfig was called"])
    infile = open('.\\config.ini', 'r')
    lines = infile.read().split('\n')
    options = dict()
    for line in lines:
        if line == '':
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
    initInputFile(options)
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


def initInputFile(options):
    global inputFile
    if 'Input file' in options.keys():
        if 'Input file' in options.keys():
            logger.backlogAppend(4, 'A valid option for log file was found in the configfile!')
            temp = options['Input file'].replace("\\","/")
            inputFile = temp
        else:
            inputFile = ".\\main.log"
            logger.backlogAppend(2, "No valid option for log file was found in the config file!")
            logger.backlogAppend(2, "Defaulting to .\\main.log!")
    logger.backlogAppend(5, "inputFile set to: " + str(inputFile))


def initLogConsole(options):
    if 'Output log type' in options.keys():
        if options['Output log type'].upper() == 'CONSOLE':
            logger.backlogAppend(4, 'A valid option for logging target was found in the config file!')
            logger.logToConsole = True
        elif options['Output log type'].upper() == 'FILE':
            logger.backlogAppend(4, 'A valid option for logging target was found in the config file!')
            logger.logToConsole = False
        else:
            logger.backlogAppend(2, "No valid option for logging target was found in the config file!")
            logger.backlogAppend(2, "Defaulting to FILE")
            logger.logToConsole = False
    logger.backlogAppend(5, "logConsole set to: " + str(logger.logToConsole))


def initLogFile(options):
    global logFile
    if 'Output log file' in options.keys():
        if 'Output log file' in options.keys():
            logger.backlogAppend(4, 'A valid option for log file was found in the configfile!')
            temp = options['Output log file'].replace("\\","/")
            logFile = temp
        else:
            logFile = ".\\main.log"
            logger.backlogAppend(2, "No valid option for log file was found in the config file!")
            logger.backlogAppend(2, "Defaulting to .\\main.log!")
    logger.backlogAppend(5, "logFile set to: " + str(logFile))


def initArgs(arguments):
    global quiet
    logger.backlog.append([3, "Function initArgs was called"])
    if '-q' in arguments or '-Q' in arguments:
        logger.log(4, 'Entering Quiet execution mode')
        quiet = True
    else:
        logger.log(4, 'Entering interactive execution mode')
        quiet = False
    logger.backlogAppend(5, "quiet set to: " + str(quiet))


class Navbar(tkinter.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        label = tkinter.Label(self, text="test")
        label.pack()


class Application(tkinter.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.navbar = Navbar(self)
        self.navbar.pack()


class fileSelector(tkinter.Frame):
    def __init__(self):
        tkinter.Frame.__init__(self, padx=10, pady=10)
        self.master.title("Example")
        self.master.rowconfigure(6, weight=1)
        self.master.columnconfigure(7, weight=1)
        self.grid(sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)

        label = tkinter.Label(self, text="Please select a file, or commit to the pre-configured one, and press OK.")
        label.grid(row=1, column=1, columnspan=7)

        self.filePath = tkinter.StringVar()
        if logFile:
            self.filePath.set(inputFile)
        filePathEntry = tkinter.Entry(self, textvariable=self.filePath)
        filePathEntry.grid(row=3, column=2, columnspan=4, sticky=(tkinter.W, tkinter.E))

        browseButton = tkinter.Button(self, text="...", command=self.browseFile, width=3)
        browseButton.grid(row=3, column=6, sticky=tkinter.W)

        okButton = tkinter.Button(self, text="OK", command=self.OK, width=10)
        okButton.grid(row=5, column=5, sticky=tkinter.W)

        cancelButton = tkinter.Button(self, text="Cancel", command=self.cancel, width=10)
        cancelButton.grid(row=5, column=2, sticky=tkinter.W)

    def browseFile(self):
        fname = tkinter.filedialog.askopenfilename(filetypes=(("Logfiles", "*.log;*.txt"), ("All files", "*.*") ))
        if fname:
            try:
                self.filePath.set(fname)
            except:
                tkinter.messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % fname)
            return

    def OK(self):
        global quit, logFile
        logFile = self.filePath.get()
        quit = False
        self.master.destroy()

    def cancel(self):
        global quit
        quit = True
        self.master.destroy()


logger = Logmanager()
logger.backlogAppend(1, "###### VSFTPD log Analyzer started ######")

initConfig()
initArgs(sys.argv)
logger.backlogFlush()

if not quiet:
    fileSelector().mainloop()

    if not quit:
        analyseLogfile()
        print('test')

        root = tkinter.Tk()
        root.title = "Super Awesome Log Analyser"
        Application(root).pack(side="top", fill="both", expand=True)
        root.mainloop()