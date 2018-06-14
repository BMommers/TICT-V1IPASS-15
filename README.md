# TICT-V1IPASS-15

This logfile analyser was written for a project at the Hogeschool Utrecht, The Netherlands.

## Prerequisites

For this program to run correctly, it requires for a correct installation of Python 3.6.
All used modules are default in Python 3.6, but are listed down here just in case.


```
import datetime, tkinter, sys
import tkinter.filedialog, tkinter.messagebox, tkinter.ttk
```

## Files
In this repo you'll find a couple of files. Below is the use of all described

[Root]

- **config.ini** - Is used for the configuration of the application. 
These settings will be used whe the application is called with the silent switch
- **main.log** - This is the default logfile for the application. Can be used for troubleshooting purposes. 
Configuration can be set in the config.ini file.
- **main.py** - The actual application. Run with python 3.6

[input]

- **vsftpd.log** - Template logfile for analysing purposes
## Built With

* [Jetbrains IntelliJ](https://www.jetbrains.com/idea/) - The IDE used
* [Git](https://maven.apache.org/) - Version control
* [GitHub](https://github.com) - Used for offsite storage and distribution

## Authors

* **Bart Mommers** - Author and Developer