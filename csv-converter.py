# Used to extract info from some csvs n stuff
# Made by Lucas Ramos-Strankman for TugboatLogic
# Jan 2021


file = "mycsv.csv"

# load csv
# Strip into Evidence ID, SOC 2, and ISO columns
# Make Dictionaries for each framework, Dict {control -> (EIDs)}

# for eval framework 1 to framework 2:
# List all unique EIDS in 1
# For each control in 2: Compare EIDs with ones in dict
# if all are in, then is fully done
# if only some, then partially done
# if none, then needs to be done
# Record EIDs not done separately to show off later

# Dispaly info meaningfully w/ matplotlib ideally

# NOTE:  some may be duplicates.


print("Hello World")
