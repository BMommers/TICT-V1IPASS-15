import datetime, tkinter, sys, tkinter.filedialog, tkinter.messagebox, configparser, operator, tkinter.ttk


class Logmanager:
    defaultThreshold = 2
    defaultFile = "main.log"
    defaultLogToConsole = False

    def __init__(self):
        self.threshold = Logmanager.defaultThreshold
        self.file = Logmanager.defaultFile
        self.logToConsole = Logmanager.defaultLogToConsole
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
    fileObject = open(config.inputFile, 'r')

    ftpCount = 0
    connectCount = 0

    clientCount = 0
    okCount = 0
    failCount = 0

    loginCount = 0
    downloadCount = 0

    failDownloadCount = 0

    for line in fileObject:
        data = line.split(" ")
        if data[8] == "CONNECT:":
            connectCount += 1
            if data[9] == "Client":
                clientCount += 1
                Client.new(data[10].split(":")[3][:-2])
            else:
                print(data)
        else:
            if data[9] == "OK":
                okCount += 1
                username = data[8][1:-1]
                if data[10] == "LOGIN:":
                    loginCount += 1
                elif data[10] == "DOWNLOAD:":
                    downloadCount += 1
                    path = "/".join(data[13].replace('"',"").split("/")[0:-1])
                    filename = data[13].replace('"',"").split("/")[-1][:-1]
                    speed = float(data[-1][:-10])
                    User.logon(username).downloadFile(path,filename, speed, True)
                else:
                    print(data[10])
            elif data[9] == "FAIL":
                failCount += 1
                if data[10] == "DOWNLOAD:":
                    failDownloadCount += 1
                    speed = float(data[-1][:-10])
                    if speed == 0.00:
                        print(data)
                        path = "/".join(data[13].replace('"',"").split("/")[0:-1])
                        filename = data[13].replace('"',"").split("/")[-1][:-1]
                        File.download(path,filename, speed, False)
                else:
                    print(data)
            else:
                print(data)
    print("analysis is complete")
    print("connectCount:" + str(connectCount))
    print("ftpCount:" + str(ftpCount))
    print("clientCount: " + str(clientCount))
    print("clients: " + str(Client.toString()))
    print("okCount: " + str(okCount))
    print("failCount: " + str(failCount))
    print("loginCount: " + str(loginCount))
    print("downloadCount: " + str(downloadCount))
    print("Average downloadSpeed:" + str(File.averageDown()))
    for file in File.sortFiles(File.existingFiles)[:10]:
        print("Attempts:\t" + str(file.downloadAttempts) + "\t" + file.filename)
    print("failDownloadCount: " + str(failDownloadCount))
    for file in File.nonExistingFiles:
        print("Not Existing:\t" + str(file.downloadAttempts) + "\t" + file.path + "\t"+ file.filename)
    for user in User.allUsers:
        print("User:\t" + user.name + "\t" + "LogonAttempts:\t" + str(user.logonAttempts))



class User:
    allUsers = []

    def __init__(self, name):
        User.allUsers.append(self)
        self.name = name
        self.logonAttempts = 0
        self.downloadedFiles = []

    def downloadFile(self, path, filename, speed, exists):
        self.downloadedFiles.append(File.download(path, filename, speed, exists))

    @staticmethod
    def logon(name):
        if not User.exist(name):
            user = User(name)
            user.logonAttempts += 1
        else:
            user = User.search(name)
            user.logonAttempts += 1
        return user


    @staticmethod
    def exist(name):
        for user in User.allUsers:
            if user.name == name:
                return True
        return False

    @staticmethod
    def search(name):
        for user in User.allUsers:
            if user.name == name:
                return user

    @staticmethod
    def toString():
        res = []
        for user in User.allUsers:
            res.append(user.name)
        return res


class Client:
    allClients = []

    def __init__(self, ip):
        self.ip = ip
        Client.allClients.append(self)

    @staticmethod
    def new(ip):
        if not Client.exist(ip):
            Client(ip)

    @staticmethod
    def exist(ip):
        for client in Client.allClients:
            if client.ip == ip:
                return True
        return False

    @staticmethod
    def toString():
        res = []
        for client in Client.allClients:
            res.append(client.ip)
        return res


class File:
    existingFiles = []
    nonExistingFiles = []
    accDownloadSpeed = 0
    totalDownloads = 0

    def __init__(self, path, filename, exists):
        self.path = path
        self.filename = filename
        self.downloadAttempts = 0
        self.exists = exists
        if self.exists:
            File.existingFiles.append(self)
        else:
            File.nonExistingFiles.append(self)

    def downloaded(self, speed):
        self.downloadAttempts += 1
        File.accDownloadSpeed += speed
        File.totalDownloads += 1

    def toString(self):
        return self.filename

    @staticmethod
    def sortFiles(list):
        newList = sorted(list, key=lambda file: file.downloadAttempts, reverse=True)
        return newList


    @staticmethod
    def download(path, filename, speed, exists):
        if not File.exist(path, filename):
             file = File(path, filename, exists)
        else:
            file = File.search(path, filename)
        file.downloaded(speed)
        return file

    @staticmethod
    def exist(path, filename):
        for file in File.existingFiles:
            if file.path == path and file.filename == filename:
                return True
        for file in File.nonExistingFiles:
            if file.path == path and file.filename == filename:
                return True
        return False

    @staticmethod
    def search(path, filename):
        for file in File.existingFiles:
            if file.path == path and file.filename == filename:
                return file
        for file in File.nonExistingFiles:
            if file.path == path and file.filename == filename:
                return file

    @staticmethod
    def averageDown():
        avg = File.accDownloadSpeed / File.totalDownloads
        rounded = "{0:.2f}".format(avg)
        return str(rounded) + " Kbyte/sec"

    @staticmethod
    def toString():
        res = []
        for file in File.existingFiles:
            res.append(file.path + file.filename)
        return res


class configParser:

    def __init__(self, file):
        logger.backlog.append([3, "Function initConfig was called"])
        infile = open(file, 'r')
        lines = infile.read().split('\n')
        options = dict()
        for line in lines:
            if line == '' or line[0] == '[' or line[0] == '#':
                continue
            if len(line.split(': ')) == 1:
                key, option = line.split(':')
            else:
                key, option = line.split(': ')
            options[key] = option

        self.loggingThreshold = configParser.initLoggingThreshold(options)
        self.logFile = configParser.initLogFile(options)
        self.inputFile = configParser.initInputFile(options)
        self.logConsole = configParser.initLogConsole(options)

        # Commandline arguments
        self.interactive = configParser.initInteractive(sys.argv)

    @staticmethod
    def initLoggingThreshold(options):
        switch = {
            'NONE': 0,
            'ERROR': 1,
            'WARN': 2,
            'INFO': 3,
            'LOG': 4,
            'DEBUG': 5
        }
        if 'Logging threshold' in options.keys():
            if options['Logging threshold'] in switch.keys():
                logger.backlogAppend(4, 'A valid option for logging threshold was found in the configfile!')
                logger.threshold = switch.get(options['Logging threshold'])
            else:
                logger.threshold = 2
                logger.backlogAppend(2, "No valid option for logging threshold was found in the config file!")
                logger.backlogAppend(2, "Defaulting to level 2, errors amd warnings only!")
        else:
            logger.threshold = 2
            logger.backlogAppend(2, "Logging threshold was not defined in the config file!")
            logger.backlogAppend(2, "Defaulting to level 2, errors amd warnings only!")
        logger.backlogAppend(5, "loggingThreshold set to: " + str(logger.threshold))
        return logger.threshold

    @staticmethod
    def initInputFile(options):
        global inputFile
        if 'Input file' in options.keys():
            if 'Input file' in options.keys():
                logger.backlogAppend(4, 'A valid option for input file was found in the configfile!')
                inputFile = options['Input file'].replace("\\","/")
            else:
                inputFile = ".\\main.log"
                logger.backlogAppend(2, "No valid option for input file was found in the config file!")
                logger.backlogAppend(2, "Defaulting to .\\input\\vsftpd.log!")
        logger.backlogAppend(5, "inputFile set to: " + str(inputFile))
        return inputFile

    @staticmethod
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
        return logger.logToConsole

    @staticmethod
    def initLogFile(options):
        global logFile
        if 'Output log file' in options.keys():
            if 'Output log file' in options.keys():
                logger.backlogAppend(4, 'A valid option for log file was found in the configfile!')
                logFile = options['Output log file'].replace("\\","/")
            else:
                logFile = ".\\main.log"
                logger.backlogAppend(2, "No valid option for log file was found in the config file!")
                logger.backlogAppend(2, "Defaulting to .\\main.log!")
        logger.backlogAppend(5, "logFile set to: " + str(logFile))
        return logFile

    @staticmethod
    def initInteractive(args):
        logger.backlog.append([3, "Function initArgs was called"])
        if '-q' in args or '-Q' in args:
            logger.log(4, 'Entering Quiet execution mode')
            interactive = False
        else:
            logger.log(4, 'Entering interactive execution mode')
            interactive = True
        logger.backlogAppend(5, "quiet set to: " + str(interactive))
        return interactive


class treeviewFiles(tkinter.Frame):
    def __init__(self, parent, list):
        self.parent = parent
        super().__init__(self.parent)

        treeview = tkinter.ttk.Treeview(self, selectmode="browse")
        treeview["columns"] = ("One", "Two")
        treeview.heading("Two", text="Attempts")
        treeview.heading("One", text="File")

        vsb = tkinter.ttk.Scrollbar(self, orient="vertical", command=treeview.yview)
        vsb.pack(side="right", fill="y")
        treeview.configure(yscrollcommand=vsb.set)

        for file in list:
            if not treeview.exists(file.path):
                treeview.insert("", "end", file.path, text=file.path, open=True)
            treeview.insert(file.path, "end", text="", values=(file.filename, file.downloadAttempts))
        treeview.pack(fill=tkinter.BOTH, expand=True)


class menu(tkinter.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # create a pulldown menu, and add it to the menu bar
        filemenu = tkinter.Menu(self, tearoff=0)
        filemenu.add_command(label="Open logfile", command=self.open)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.close)
        self.add_cascade(label="File", menu=filemenu)

        # create more pulldown menus
        viewmenu = tkinter.Menu(self, tearoff=0)
        viewmenu.add_command(label="Top 10 downloaded files", command=self.master.viewDownloadedFiles)
        viewmenu.add_command(label="Missende bestanden", command=self.master.viewNonExistingFiles)
        viewmenu.add_command(label="Paste")
        self.add_cascade(label="View", menu=viewmenu)

        helpmenu = tkinter.Menu(self, tearoff=0)
        helpmenu.add_command(label="About")
        self.add_cascade(label="Help", menu=helpmenu)

    def open(self):
        global closeApp
        closeApp = False
        self.master.master.destroy()


class Application(tkinter.Frame):
    def __init__(self):
        tkinter.Frame.__init__(self, padx=10, pady=10)
        self.grid(sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
        self.master.title("VSFTPD Log analyser")

        self.master.resizable(width=False, height=True)
        self.rowconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)

        navbar = menu(self)
        self.master.config(menu=navbar)

        self.nonExistingFiles = treeviewFiles(self, File.sortFiles(File.nonExistingFiles))

        self.downloadedFiles = treeviewFiles(self, File.sortFiles(File.existingFiles)[:10])

        self.viewDownloadedFiles()

    def emptyScreen(self):
        list = self.pack_slaves()
        for l in list:
            l.pack_forget()

    def viewDownloadedFiles(self):
        self.emptyScreen()
        tkinter.Label(self, text="Most downloaded files").pack()
        self.downloadedFiles.pack()

    def viewNonExistingFiles(self):
        self.emptyScreen()
        tkinter.Label(self, text="Failed download Attempts").pack()
        self.nonExistingFiles.pack()


    def close(self):
        global closeApp
        print("CLOSING APP")
        closeApp = True
        self.master.destroy()


class fileSelector(tkinter.Frame):
    def __init__(self):
        global closeApp
        tkinter.Frame.__init__(self, padx=10, pady=10)
        self.master.title("File locator")

        self.master.resizable(width=False, height=False)
        self.master.rowconfigure(6, weight=1)
        self.master.columnconfigure(7, weight=1)
        self.grid(sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)

        label = tkinter.Label(self, text="Please select a file, or commit to the pre-configured one, and press OK.")
        label.grid(row=1, column=1, columnspan=7)

        self.filePath = tkinter.StringVar()
        self.filePath.set(config.inputFile)

        filePathEntry = tkinter.Entry(self, textvariable=self.filePath)
        filePathEntry.grid(row=3, column=2, columnspan=4, sticky=(tkinter.W, tkinter.E))

        browseButton = tkinter.Button(self, text="...", command=self.browseFile, width=3)
        browseButton.grid(row=3, column=6, sticky=tkinter.W)

        okButton = tkinter.Button(self, text="OK", command=self.OK, width=10)
        okButton.grid(row=5, column=5, sticky=tkinter.W)

        cancelButton = tkinter.Button(self, text="Cancel", command=self.cancel, width=10)
        cancelButton.grid(row=5, column=2, sticky=tkinter.W)

        closeApp = True

    def browseFile(self):
        fname = tkinter.filedialog.askopenfilename(filetypes=(("Logfiles", "*.log;*.txt"), ("All files", "*.*") ))
        if fname:
            try:
                self.filePath.set(fname)
            except:
                tkinter.messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % fname)
            return

    def OK(self):
        global closeApp, logFile
        logFile = self.filePath.get()
        closeApp = False
        self.master.destroy()

    def cancel(self):
        global closeApp
        closeApp = True
        self.master.destroy()


def init():
    global closeApp
    closeApp = False
    while not closeApp:
        if config.interactive:
            fileSelector().mainloop()
            if closeApp:
                sys.exit()

            closeApp = True

            analyseLogfile()
            Application().mainloop()
        else:
            print("DO SILENT STUFF")


logger = Logmanager()
logger.backlogAppend(1, "###### VSFTPD log Analyzer started ######")

config = configParser('.\\config.ini')
logger.backlogFlush()


init()