import datetime
import tkinter
import sys
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk


class Logmanager:
    """ Logmanager class is used for managing the connection to the logfile.
    Its methods can be called to write to the logs."""
    defaultThreshold = 2
    defaultFile = "main.log"
    defaultLogToConsole = False
    template = {
        0: "NONE",
        1: "ERROR",
        2: "WARN",
        3: "INFO",
        4: "LOG ",
        5: "DEBUG"
    }

    def __init__(self):
        """ Initializer method for the Logmanager class. Sets all instance variables"""
        self.threshold = Logmanager.defaultThreshold
        self.file = Logmanager.defaultFile
        self.logToConsole = Logmanager.defaultLogToConsole
        self.backlog = []

    def backlogAppend(self, level, message):
        """ While the configParser is busy reading and iterpreting the configfile, the backlog can be used to save
         messages until they are ready to be Written to the file, or to be printed to the screen"""
        self.backlog.append([level, message])

    def backlogFlush(self):
        """ Method is used to empty the backlog to specified media"""
        for log in self.backlog:
            self.print(log[0], log[1])

    @staticmethod
    def formatter(message, level):
        """ Makes sure all messages are formatted in exactly the same manner """
        timestamp = str(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"))
        return timestamp + "\t" + Logmanager.template.get(level) + "\t" + message

    def print(self, level, message):
        """ Is used to write messages to preffered media once the config has been initialized """
        if self.threshold >= level and self.threshold != 0:
            # If specified threshold is above 0, and higher than the level of the message, the message will be processed
            message = self.formatter(message, level)
            if self.logToConsole:  # If configfile states that messages should be printed to the screen
                print(message)
            else:  # If messages should not be printed to the screen
                file = open(self.file, "a")
                file.write(message + "\n")
                file.close()


def analyseLogfile():
    """ Function analyses the specified logfile, and takes all important information before saving it """
    global closeApp
    logger.print(3, "analyseLogfile was called")
    fileObject = open(config.inputFile, 'r')
    for event in fileObject:  # For every line in specified logfile
        try:
            data = event.split(" ")
            if data[8] == "CONNECT:":  # Message is a CONNECT event
                if data[9] == "Client":  # With a specified client, save the data into a new client object
                    Client.new(data[10].split(":")[3][:-2])
                else:  # A new type of event will be logged to the logfile
                    logger.print(4, "An unknown connect event was found")
                    logger.print(2, "Event was not recognized")
                    logger.print(2, data)
            else:  # Message is a user-initiated event
                if data[9] == "OK":  # Events status is OK
                    username = data[8][1:-1]
                    if data[10] == "DOWNLOAD:":  # Event is a  download event
                        path = "/".join(data[13].replace('"', "").split("/")[0:-1])
                        filename = data[13].replace('"', "").split("/")[-1][:-1]
                        speed = float(data[-1][:-10])
                        size = int(data[-3])
                        # Username logs in as an object, and downloads specified file
                        User.logon(username).downloadFile(path, filename, speed, True, size)
                    elif data[10] == "LOGIN:":  # If message is a LOGON event, do nothing
                        continue
                    else:   # A new type of event will be logged to the logfile
                        logger.print(4, "An unknown connect event was found")
                        logger.print(2, "Event was not recognized")
                        logger.print(2, data)
                elif data[9] == "FAIL":  # If the event states a failed action
                    if data[10] == "DOWNLOAD:":  # if the event is a download event
                        speed = float(data[-1][:-10])
                        if speed == 0.00:  # And the speed equals zero
                            path = "/".join(data[13].replace('"', "").split("/")[0:-1])
                            filename = data[13].replace('"', "").split("/")[-1][:-1]
                            #  Save the event as an object
                            File.download(path, filename, speed, False)
                    else:  # A new type of event will be logged to the logfile
                        logger.print(4, "An unknown connect event was found")
                        logger.print(2, "Event was not recognized")
                        logger.print(2, data)
                else:  # A new type of event will be logged to the logfile
                    logger.print(4, "An unknown connect event was found")
                    logger.print(2, "Event was not recognized")
                    logger.print(2, data)
        except:
            logger.print(1, "File could not be processed.")
            logger.print(1, "Error occured while processing the following line:.")
            logger.print(1, event)
            raise ValueError('File could not be processed. Check the logFile!')


class User:
    """ User class is used for saving users who logged on to the vsftpd server
     There is no difference between anonymous logged in users, or the default ftp user"""
    allUsers = []

    def __init__(self, name):
        """ Initiator method for user objects """
        User.allUsers.append(self)
        self.name = name
        self.logonAttempts = 0
        self.downloadedFiles = []
        self.totaldownloadedBytes = 0

    def downloadFile(self, path, filename, speed, exists, size):
        """User downloads a file, which gets saved to its own downloadedFiles list"""
        self.downloadedFiles.append(File.download(path, filename, speed, exists))
        #  totaldownloadedbytes are saved
        self.totaldownloadedBytes += size

    @staticmethod
    def logon(name):
        """ Method for logging in new or existing users"""
        if not User.exist(name):  # If the user does not yet exist, create him
            user = User(name)
            user.logonAttempts += 1
        else:  # If the user DOES exits, find him and log the logon attempts
            user = User.search(name)
            user.logonAttempts += 1
        return user  # return the user

    @staticmethod
    def exist(name):
        """ Check if the username has logged on before """
        for user in User.allUsers:
            if user.name == name:  # If user logged on before, return true
                return True
        return False   # otherwise, return False

    @staticmethod
    def search(name):
        """ Find an existing user by name """
        for user in User.allUsers:
            if user.name == name:
                return user  # return found user


class Client:
    """ A client class for creating client objects.
    Has no specific use for now, but may be implemented further in the future """
    allClients = []

    def __init__(self, ip):
        """ Initiator method for creating client objects """
        self.ip = ip
        self.sessions = 1
        Client.allClients.append(self)

    @staticmethod
    def new(ip):
        """ If client does not exist, create the new client """
        if not Client.exist(ip):
            Client(ip)
        else:
            Client.search(ip).sessions += 1

    @staticmethod
    def exist(ip):
        """ Checks if specified client already exists or not """
        for client in Client.allClients:
            if client.ip == ip:
                return True  # Return true, if client exists
        return False  # Return false if client does not exist

    @staticmethod
    def search(ip):
        """ Method for searching and returning an existing client """
        for client in Client.allClients:
            if client.ip == ip:   # If file is found in allClients list return it
                return client


class File:
    """ File class for creating and saving file objects """
    existingFiles = []
    nonExistingFiles = []
    accDownloadSpeed = 0
    totalDownloads = 0

    def __init__(self, path, filename, exists):
        """ initiator method for creating File objects """
        self.path = path
        self.filename = filename
        self.downloadAttempts = 0
        self.exists = exists
        if self.exists:  # If file was found on the server, add itself for ExistingFiles list
            File.existingFiles.append(self)
        else:  # If file was not found on the server, add itself to the nonExisting File list
            File.nonExistingFiles.append(self)

    def downloaded(self, speed):
        """ Keeps track of how many times a file was downloaded """
        self.downloadAttempts += 1   # File was downloaded once
        File.accDownloadSpeed += speed   # Add download speed to accumulatedDownloadSpeed Static variable
        File.totalDownloads += 1  # Total downloads gets incremented

    @staticmethod
    def sortFiles(lst):
        """ Sort specified list of files according to their amount of downloadAttempts """
        newList = sorted(lst, key=lambda file: file.downloadAttempts, reverse=True)
        return newList  # Return the newly created list

    @staticmethod
    def download(path, filename, speed, exists):
        """ Method for recording the download of a file """
        if not File.exist(path, filename):  # If the file does not exist, create it
            file = File(path, filename, exists)
        else:   # If the file exists, Search for the object
            file = File.search(path, filename)
        file.downloaded(speed)  # Save the download of said file
        return file  # Return the file

    @staticmethod
    def exist(path, filename):
        """ Check if a file exists based off of the path and the filename """
        for file in File.existingFiles:
            if file.path == path and file.filename == filename:  # If file is found in existingFiles return true
                return True
        for file in File.nonExistingFiles:
            if file.path == path and file.filename == filename:  # If file is found in nonExistingFiles, return TRue
                return True
        return False  # IF file is not found, return False

    @staticmethod
    def search(path, filename):
        """ Method for searching and returning an existing file """
        for file in File.existingFiles:
            if file.path == path and file.filename == filename:   # If file is found in existingFiles return true
                return file
        for file in File.nonExistingFiles:
            if file.path == path and file.filename == filename:  # If file is found in nonExistingFiles, return TRue
                return file

    @staticmethod
    def averageDown():
        """ Calculates and returns the average download speed, rounded to 2 decimals """
        avg = File.accDownloadSpeed / File.totalDownloads
        rounded = "{0:.2f}".format(avg)
        return str(rounded) + " Kbyte/sec"


class configParser:
    """ class for interpreting and saving the configuration as found in the config file """

    def __init__(self, file):
        """ initiater method for the configparser """
        logger.print(3, "configParser is initialized")
        infile = open(file, 'r')
        lines = infile.read().split('\n')
        options = dict()
        for line in lines:
            if line == '' or line[0] == '[' or line[0] == '#':  # if line is empty or marked with a comment marker
                continue
            if len(line.split(': ')) == 1:  # If there's no space after the :
                key, option = line.split(':')   # Split it without a space
            else:   # If there's a space after the :
                key, option = line.split(': ')  # split at : and remove the space
            options[key] = option   # Safe the options in a dictionary and resolve them later

        # Save all options as instance variabels for later reference
        self.loggingThreshold = configParser.initLoggingThreshold(options)
        self.logFile = configParser.initLogFile(options)
        self.inputFile = configParser.initInputFile(options)
        self.logConsole = configParser.initLogConsole(options)

        # Commandline arguments
        self.interactive = configParser.initInteractive(sys.argv)

    @staticmethod
    def initLoggingThreshold(options):
        """ Read the loggingThreshold parameter from the configFile and translate it to a valid value """
        logger.print(3, "initLoggingThreshold method is called")
        switch = {
            'NONE': 0,
            'ERROR': 1,
            'WARN': 2,
            'INFO': 3,
            'LOG': 4,
            'DEBUG': 5
        }
        if 'Logging threshold' in options.keys():   # If this option has been specified in the options
            if options['Logging threshold'] in switch.keys():   # If the specified value is valid
                logger.backlogAppend(4, 'A valid option for logging threshold was found in the configfile!')
                logger.threshold = switch.get(options['Logging threshold'])  # Save the valid level in the logmanager
            else:   # If no valid value has been found, resort to the default value of 2
                logger.threshold = 2
                logger.backlogAppend(2, "No valid option for logging threshold was found in the config file!")
                logger.backlogAppend(2, "Defaulting to level 2, errors amd warnings only!")
        else:  # If no valid value has been found, resort to the default value of 2
            logger.threshold = 2
            logger.backlogAppend(2, "Logging threshold was not defined in the config file!")
            logger.backlogAppend(2, "Defaulting to level 2, errors amd warnings only!")
        logger.backlogAppend(5, "loggingThreshold set to: " + str(logger.threshold))
        return logger.threshold  # return interpreted value

    @staticmethod
    def initInputFile(options):
        """ Read the inputFile parameter from the configFile and translate it to a valig value"""
        logger.backlogAppend(3, "initInputFile method is called")
        if 'Input file' in options.keys():  # If this option has been specified in the options
            if 'Input file' in options.keys():   # If the specified value is valid
                logger.backlogAppend(4, 'A valid option for input file was found in the configfile!')
                inputFile = options['Input file'].replace("\\", "/")
            else:  # If no valid value has been found, resort to the default value
                inputFile = ".\\main.log"
                logger.backlogAppend(2, "No valid option for input file was found in the config file!")
                logger.backlogAppend(2, "Defaulting to .\\input\\vsftpd.log!")
        else:  # If no valid value has been found, resort to the default value
            inputFile = ".\\main.log"
            logger.backlogAppend(2, "No valid option for input file was found in the config file!")
            logger.backlogAppend(2, "Defaulting to .\\input\\vsftpd.log!")
        logger.backlogAppend(5, "inputFile set to: " + str(inputFile))
        return inputFile  # Return the interpreted value

    @staticmethod
    def initLogConsole(options):
        """  Read the logConsole parameter from the configFile and translate it to a valid value """
        logger.backlogAppend(3, "initLogConsole method is called")
        if 'Output log type' in options.keys():   # If this option has been specified in the options
            if options['Output log type'].upper() == 'CONSOLE':   # If the specified value is CONSOLE
                logger.backlogAppend(4, 'A valid option for logging target was found in the config file!')
                logger.logToConsole = True  # Log data to the console
            elif options['Output log type'].upper() == 'FILE':   # If the specified value is FILE
                logger.backlogAppend(4, 'A valid option for logging target was found in the config file!')
                logger.logToConsole = False  # log data to a file
            else:  # If no valid value has been found, resort to the default value
                logger.backlogAppend(2, "No valid option for logging target was found in the config file!")
                logger.backlogAppend(2, "Defaulting to FILE")
                logger.logToConsole = False     # log data to a file
        logger.backlogAppend(5, "logConsole set to: " + str(logger.logToConsole))
        return logger.logToConsole

    @staticmethod
    def initLogFile(options):
        """  Read the logFile parameter from the configFile and translate it to a valid value """
        logger.backlogAppend(3, "initLogFile method is called")
        if 'Output log file' in options.keys():   # If this option has been specified in the options
            logger.backlogAppend(4, 'A valid option for log file was found in the configfile!')
            file = options['Output log file'].replace("\\", "/")
        else:  # If no valid value has been found, resort to the default value
            file = ".\\main.log"
            logger.backlogAppend(2, "No valid option for log file was found in the config file!")
            logger.backlogAppend(2, "Defaulting to .\\main.log!")
        logger.backlogAppend(5, "logFile set to: " + str(file))
        logger.file = file
        return file  # return the file location

    @staticmethod
    def initInteractive(args):
        """  Read the commandline parameter translate it to a valid configuration  """
        logger.backlogAppend(3, "initInteractive method is called")
        if '-q' in args or '-Q' in args:    # If Q switch is specified
            logger.backlogAppend(4, 'Entering Quiet execution mode')
            interactive = False     # Enter quiet mode
            logger.backlogAppend(5, "interactive was set to " + str(interactive))
        else:   # If Q switch is not specified
            logger.backlogAppend(4, 'Entering interactive execution mode')
            interactive = True   # Enter interactive mode
            logger.backlogAppend(5, "interactive was set to " + str(interactive))
        return interactive  # Return the option


class treeviewFiles(tkinter.Frame):
    """ Class is used for creating treeview Objects, to be used to display data about files """

    def __init__(self, parent, lst):
        """ Initiator needs a parent in which this object is to be created, and a list of files to fill the fields """
        logger.print(3, "treeviewFiles init method was called")
        self.parent = parent
        super().__init__(self.parent)

        treeview = tkinter.ttk.Treeview(self, selectmode="browse")
        # Create and initialize the columns for the treeview
        treeview["columns"] = ("One", "Two")
        treeview.heading("Two", text="Attempts")
        treeview.heading("One", text="File")

        # Create a scrollbar object and link it to the treeview yview command
        vsb = tkinter.ttk.Scrollbar(self, orient="vertical", command=treeview.yview)
        vsb.pack(side="right", fill="y")    # Add the scrolbar to the Frame
        treeview.configure(yscrollcommand=vsb.set)  # Link the treeview yscroll command to the scrollbar

        for file in lst:    # For evey file in the list
            if not treeview.exists(file.path):  # If there is no key ( directory ) for the path, create it
                # Create a "directory" in which other data can be put. The ID is the ID
                treeview.insert("", "end", file.path, text=file.path, open=True)
            # Insert all data of the file to the "directory" of the corresponding path.
            # file.path is used to select the id of the "directory"
            treeview.insert(file.path, "end", text="", values=(file.filename, file.downloadAttempts))
        treeview.pack(fill=tkinter.BOTH, expand=True)  # Add the treeview object to the frame


class userOverview(tkinter.Frame):
    """ Class is used to create a treeview userOverview to be used in the application"""
    def __init__(self, parent):
        """ Initiator needs a tkinterparent to place itself into """
        logger.print(3, "userOverview init method was called")
        self.parent = parent
        super().__init__(self.parent)

        treeview = tkinter.ttk.Treeview(self, selectmode="browse")
        # Create and initialize the columns of the treeview object
        treeview["columns"] = ("One", "Two")
        treeview.heading("One", text="Total Bytes")
        treeview.heading("Two", text="Logon attempts")

        # Create a scrollbar object and link it to the yview command of the treeview object
        vsb = tkinter.ttk.Scrollbar(self, orient="vertical", command=treeview.yview)
        # Pack the scrollbar to the Frame
        vsb.pack(side="right", fill="y")
        #   Configure treeview to present its yvalue to the scrollbar
        treeview.configure(yscrollcommand=vsb.set)

        for user in User.allUsers:      # For all users
            bts = str(user.totaldownloadedBytes) + " KBytes",
            # Create a new treeview key, containing all interesting data from that user
            treeview.insert("", "end", text=user.name, values=(bts, user.logonAttempts))
        #  Pack the treeview to the frame
        treeview.pack(fill=tkinter.BOTH, expand=True)


class clientOverview(tkinter.Frame):
    """ Class is used to create an overview of all clients to be used in the application"""
    def __init__(self, parent):
        """ Initiator needs a tkinterparent to place itself into """
        logger.print(3, "userOverview init method was called")
        self.parent = parent
        super().__init__(self.parent)

        treeview = tkinter.ttk.Treeview(self, selectmode="browse")
        # Create and initialize the columns of the treeview object
        treeview["columns"] = ("One", "Two")
        treeview.heading("One", text="IP")
        treeview.heading("Two", text="Sessions")

        # Create a scrollbar object and link it to the yview command of the treeview object
        vsb = tkinter.ttk.Scrollbar(self, orient="vertical", command=treeview.yview)
        # Pack the scrollbar to the Frame
        vsb.pack(side="right", fill="y")
        #   Configure treeview to present its yvalue to the scrollbar
        treeview.configure(yscrollcommand=vsb.set)

        for client in Client.allClients:      # For all clients
            # Create a new treeview key, containing all interesting data from that client
            treeview.insert("", "end", text="", values=(client.ip, client.sessions))
        #  Pack the treeview to the frame
        treeview.pack(fill=tkinter.BOTH, expand=True)


class Menu(tkinter.Menu):
    """ Menu class is user to create tkinter menu objects to fill the applications menubar """
    def __init__(self, parent):
        """ Menu objects require a parent to place itself into """
        logger.print(3, "Menu init method was called")
        super().__init__(parent)
        self.parent = parent

        # Create a Header and add commandbuttons to it
        filemenu = tkinter.Menu(self, tearoff=0)
        filemenu.add_command(label="Open logfile", command=self.open)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.close)
        self.add_cascade(label="File", menu=filemenu)

        # Create a Header and add commandbuttons to it
        viewmenu = tkinter.Menu(self, tearoff=0)
        viewmenu.add_command(label="Top 10 downloaded files", command=self.master.viewDownloadedFiles)
        viewmenu.add_command(label="Missende bestanden", command=self.master.viewNonExistingFiles)
        viewmenu.add_command(label="Overzicht gebruikers", command=self.master.viewUserOverview)
        viewmenu.add_command(label="Overzicht clients", command=self.master.viewClientOverview)
        self.add_cascade(label="View", menu=viewmenu)

        # Create a Header and add commandbuttons to it
        helpmenu = tkinter.Menu(self, tearoff=0)
        helpmenu.add_command(label="About", command=self.master.about)
        self.add_cascade(label="Help", menu=helpmenu)

    def open(self):
        """ Prep the application to be run again and start over at the beginning """
        logger.print(3, "Menu open method was called")
        global closeApp
        closeApp = False
        self.master.master.destroy()


class Application(tkinter.Frame):
    """ Application class is user to create the application and to have its own variablepool and methods """
    def __init__(self):
        """ Initiator creates all sections off the application so that they can be alled upon later """
        logger.print(3, "Application init method was called")
        tkinter.Frame.__init__(self, padx=10, pady=10)
        self.grid(sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
        self.master.title("VSFTPD Log analyser")

        self.master.resizable(width=False, height=True)
        self.rowconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)

        navbar = Menu(self)     # Create the navigation bar (menubar)
        self.master.config(menu=navbar)  # Configure the window to use the navigation bar

        #  Initiate all different views, but dont push them to the screen
        self.nonExistingFiles = treeviewFiles(self, File.sortFiles(File.nonExistingFiles))
        self.downloadedFiles = treeviewFiles(self, File.sortFiles(File.existingFiles)[:10])
        self.userOverview = userOverview(self)
        self.clientOverview = clientOverview(self)

        #   Push the most downloadedFiles treeviewobject to the screen at startup
        self.viewDownloadedFiles()

    def emptyScreen(self):
        """ Clear the screen of all objects """
        logger.print(3, "Application empytyScreen method was called")
        for s in self.pack_slaves():
            s.pack_forget()

    def viewUserOverview(self):
        """ Push the useroverview to the screen """
        logger.print(3, "Application viewUserOverview method was called")
        self.emptyScreen()
        tkinter.Label(self, text="Overzicht van alle gebruikers").pack()
        self.userOverview.pack()

    def viewDownloadedFiles(self):
        """ Push the DownloadedFilesoverview to the screen """
        logger.print(3, "Application viewDownloaddeFiles method was called")
        self.emptyScreen()
        tkinter.Label(self, text="Most downloaded files").pack()
        self.downloadedFiles.pack()

    def viewNonExistingFiles(self):
        """ Push the NonExistingoverview to the screen """
        logger.print(3, "Application viewNonExistingFiles method was called")
        self.emptyScreen()
        tkinter.Label(self, text="Failed download Attempts").pack()
        self.nonExistingFiles.pack()

    def viewClientOverview(self):
        """ Push the NonExistingoverview to the screen """
        logger.print(3, "Application viewClientOverview method was called")
        self.emptyScreen()
        tkinter.Label(self, text="Logged on clients").pack()
        self.clientOverview.pack()

    def close(self):
        """ Close the application, and configure it not to reopen it """
        logger.print(3, "Application close method was called")
        global closeApp
        closeApp = True
        self.master.destroy()

    @staticmethod
    def about():
        """ Present a message about the application """
        logger.print(3, "Application about static method was called")
        # Create a variable with only truthful information
        text = "This application was developed by Bart Mommers, " \
               "student at the Hogeschool Utrecht, The Netherlands.\n\n" \
               "Truly an amazing guy!\n\n" \
               "(He really deserves an A!)"
        tkinter.messagebox.showinfo("Title", text)


class fileSelector(tkinter.Frame):
    """  Class is used to create a fileSelector Frame object. Object enables user to select a logfile.
    This logfile is saved to the corresponding config variable"""
    def __init__(self):
        logger.print(3, "fileSelector init method was called")
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
        """ Open a browseDialog, filtered on *.log and *.txt files """
        logger.print(3, "fileSelector browseFile method was called")
        fname = tkinter.filedialog.askopenfilename(filetypes=(("Logfiles", "*.log;*.txt"), ("All files", "*.*")))
        if fname:
            try:
                self.filePath.set(fname)
            except:
                tkinter.messagebox.showerror("Open Source File", "Failed to read file\n'%s'" % fname)
            return

    def OK(self):
        """ Confirm selected path and file and save it """
        global closeApp, logFile
        logger.print(3, "fileSelector OK method was called")
        file = self.filePath.get()
        try:
            open(file, 'r')
            ext = file.split(".")[-1]
            if ext != "txt" and ext != "log":
                msg = "Op dit moment worden " + ext + " bestanden niet ondersteund. Geef een .txt of .log bestand op!"
                tkinter.messagebox.showerror("Niet ondersteund bestandstype", msg)
                return
        except OSError:
            # if the file does not exist
            tkinter.messagebox.showerror("Incorrect pad!", "Het pad wat u ingevuld heeft is incorrect!")
            return
        config.inputFile = file
        closeApp = False
        self.master.destroy()

    def cancel(self):
        """ Cancel the window and dont reopen the application"""
        logger.print(3, "fileSelector cancel method was called")
        global closeApp
        closeApp = True
        self.master.destroy()


def initInteractive():
    """ Initialize the interactive operation mode """
    logger.print(3, "initInteractive function was called")
    global closeApp
    closeApp = False
    while not closeApp:
        fileSelector().mainloop()
        if closeApp:
            sys.exit()

        analyseLogfile()
        closeApp = True

        Application().mainloop()


def initSilent():
    """  Initialize the silent operation mode """
    logger.print(3, "initSilent function was called")
    #  silent operation mode is yet to be implemented
    print("DO SILENT STUFF")


#  Initialize the logger Logmanager object, so that logs may be managed
logger = Logmanager()
logger.backlogAppend(1, "###### VSFTPD log Analyzer started ######")

#  Initialize the configParser, to read the config file and to translate it to valid configurations
config = configParser('.\\config.ini')
# Now that the config is initialized, the backlog may be flushed to the right media
logger.backlogFlush()

if config.interactive:  # If Application is to run interactively
    logger.print(4, "Application will start in Interactive mode")
    initInteractive()
elif not config.interactive:    # If application is not to run interactively
    logger.print(4, "Application will start in Silent mode")
    initSilent()
