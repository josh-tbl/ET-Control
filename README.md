# ET-Control

Code was designed to be used from the commandline
Developed for Python 2.7 as that comes stock in Mac

## How to use
Put both the script and your csv in a folder and run the script from the commandline


## Overview of how it works:
After reading the csv in, we create dictionaries for each framework.
The control name is used as a key, and leads to a list of evidence task ids.
Each control is then mapped to a list of ET ids that it requires.
Using these dictionaries, we can make lists of "implemented" ETs and see how many controls of another framework are satisfied by this list.
Finally, we can plot this information using matplotlib.
