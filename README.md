# ET-Control

Code was designed to be used from the commandline
Developed for Python 2.7 as that comes stock in Mac

## How to use
### Pre-conditions:
    - Script and CSV's in same folder
    - Python 2.7 installed and on PATH (should be default on Tugboat Logic computers)

### Running Instructions (from Command-Line):
```
    python examine_ETs.py [-i] [-v]
```
    - [-i]: Option to specify 1 "Implemented" Framework. Default Framework: NIST CSF.
    - [-v]: Option to specify at least 1 Framework to be "Investigated". Default\n Framework: ISO 27001:2013.
    - Make sure all frameworks are entered such that they are encapsulated by quotation marks.
    - e.g.
    python examine_ETs.py -i "NIST CSF (Cybersecurity Framework)" -v "HIPAA Compliance" "SOC 2"



## Overview of how it works:
After reading the csv in, we create dictionaries for each framework.
The control name is used as a key, and leads to a list of evidence task ids.
Each control is then mapped to a list of ET ids that it requires.
Using these dictionaries, we can make lists of "implemented" ETs and see how many controls of another framework are satisfied by this list.
Finally, we can plot this information using matplotlib.
