PROJECT DEPENDENCIES

- Python 2.7
- Tkinter

For this project Python 2.7 was used along with mostly pre-packaged modules.  The most likely module not to be packaged with your distribution is the tkinter gui toolbox.  There is no pip package available to my knowledge. The easiest ways to install are as follows...

On Ubuntu:
apt-get install python-tk

On Fedora:
yum install tkinter

On Mac (more complicated):
see -->  https://www.python.org/download/mac/tcltk/

I'm not aware of any other dependencies that are not normally packaged with Python 2.7 distributions.


PROJECT CONCEPT

The basic idea was to query two JSON REST APIs serving data on political campaign contributions and lobbying, respectively.  For the project, I wrote what is essentially a script with access to two api wrapper functions.  Then there is a library of functions for interfacing with the database.  Last, there is a class which provides GUI for exploring data already retrieved and stored.  Below are links to important resources (although neither is necessary to use any feature of the project submitted).

API Hompepage:  http://data.influenceexplorer.com/api/
Obtain API key:  http://sunlightfoundation.com/api/accounts/register/


PROJECT STRUCTURE

db_builder.py  --  When ran as main, executes a script which creates a new db named 'influence.db' and populates data via repeated api queries (based on a few constants provided in file).  Also contains the api wrapper functions that can be used to get contribution or lobby data.  To use as library import db_builder.

db_manager.py  --  Acts as a functional interface to communicate with dbs.  Provides connection open and close functions as well as some limited insert and query functions.

db_gui.py  --  Contains the display window class for creating a GUI browse database information.  Run as main to use GUI.

influenceXXXX.db (multiple)  --  These are the various databases with XXXX representing the four digit year.  This was a result of initially not intending look at multiple years, but later deciding that it would be cool to see a few different years without reworking the whole project to support a new schema.
