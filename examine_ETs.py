# Used to examine shared ETs between frameworks
# Made by Lucas Ramos-Strankman for TugboatLogic
# Parsing Capabilities added by Joshua Cordeiro-Zebkowitz (March 31, 2021)
# Jan 2021

# Code was designed to be used from the commandline
# Developed for Python 2.7 as that comes stock in Mac

# Overview of how it works:
# After reading the csv in, we create dictionaries for each framework
# The control name is used as a key, and leads to a list of evidence task ids
# Each control is mapped to a list of ET ids that it requires
# Using these dictionaries, we can make lists of "implemented" ETs
# and see how many controls of another framework are satisfied by this list
# Finally, we can plot this information using matplotlib

import csv
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse


# Expects a csv with the ET ids in the 1st column, and frameworks in the
# 5th onward columns
def parse_csv(filename):
    info = []
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                info.append(row)
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
    return info

# Takes the control_export as input and returns a dictionary of dictionaries
# where each dictionary is a framework in tbl. These are then dictionaries with
# their associated controls as keys mapping to empty lists
# control_export must be in csv form
def create_dict_of_frameworks(filename):
    framework_dicts = {}
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            next(reader, None) # This is to skip the header
            for row in reader:
                if row[6]: # col 6 has the frameworks, this checks it is not an empty cell
                    frameworks_list = row[6].split('\n')
                    for f in frameworks_list:
                        if f in framework_dicts:
                            framework = framework_dicts[f]
                            framework[row[1]] = [] # col 1 has the control name
                        else:
                            framework = {}
                            framework[row[1]] = []
                            framework_dicts[f] =  framework # add framework to the framework dict
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))
    return framework_dicts


# takes a dictionary of dictionaries, each representing a framework in tbl
# needs et_export in csv form
# maps ET ids to controls in each dict using et_export file
def fill_frameworks_with_ets(filename, framework_dicts):
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        try:
            next(reader, None) # This is to skip the header
            for row in reader:
                framework_list = row[8].split('\n') # col 8 has the frameworks this et is used in
                # print(framework_list)
                for f in framework_list: # for each assocaited framework
                    if f in framework_dicts:
                        framework = framework_dicts[f]
                        control_list = row[7].split('\n') # col 7 contains the associated controls to this et
                        for control in control_list: # for each associated control
                            if control in framework: # control is in this framework, find it and add the et to it
                            #     print("CONTROL IN FRAMEWORK")
                            # else:
                            #     print("NOT IN FRAMEWORK")
                                et_list = framework[control]
                                et_list.append(row[0]) # col 0 has the ET id
                    # else:
                    #     print("err: encountered a framework that was not found")
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))


# Adds the ET_id to a list for the given control, handles
# some erroneous control checking
def add_to_framework_dict(ET_id, control, framework):
    if control != "":
        if control in framework:
            ET_list = framework.get(control)
            ET_list.append(ET_id)
            framework[control] = ET_list
        else:
            framework[control] = [ET_id]


# Returns a list of implemented ET ids given a list of framework dictionaries
def find_implemented_ETs(framework_list):
    ET_set = set()
    for framework in framework_list:
        for control, control_ET_list in framework.iteritems():
            for ET_id in control_ET_list:
                ET_set.add(ET_id)
    return sorted(ET_set) # Returns a list of the ETs included in our frameworks


# Determines based on implemented_ETs whether the controls in a framework
# have been collected, patially collected, or are still outstanding, and
# returns lists of controls for each
def control_implemented_status(implemented_ETs, fw2):
    collected = []
    partial = []
    outstanding = []
    for control, control_ET_list in fw2.iteritems():
        if control == 'label': # ignores the framework name that is added to the dictionary
            continue
        if all(ET_id in implemented_ETs for ET_id in control_ET_list):
            collected.append(control)
        elif any(ET_id in implemented_ETs for ET_id in control_ET_list):
            partial.append(control)
        else:
            outstanding.append(control)
    return collected, partial, outstanding


def output_to_file(collected, partial, outstanding, framework):
    file = open(framework.replace(" ", "_") + "_Control_breakdown.txt", "w")

    file.write("Collected Controls:\n")
    for control in collected:
        file.write(control + "\n")

    file.write("\n")
    file.write("Partially Collected Controls:\n")
    for control in partial:
        file.write(control + "\n")

    file.write("\n")
    file.write("Outstanding Controls:\n")
    for control in outstanding:
        file.write(control + "\n")
    file.close()


def compare_framework_ETs(framework_list, fw2):
    implemented_ETs = find_implemented_ETs(framework_list)
    collected, partial, outstanding = control_implemented_status(implemented_ETs, fw2)
    output_to_file(collected, partial, outstanding, fw2["label"]) #outputs the results to a txt file
    col_num = len(collected)
    par_num = len(partial)
    out_num = len(outstanding)
    all_num = col_num + par_num + out_num
    print("Collected controls: {0}".format(col_num))
    print("Partially collected controls: {0}".format(par_num))
    print("Controls with unique ETs: {0}".format(out_num))
    print("Collected controls/rest = {}/{} = {:.2f}% ".format(col_num, all_num, float(col_num)/all_num*100 ))


 # Shows a single bar representing control status based on
 # one or more already implemented frameworks
 # Still in progress
def single_stacked_bar(framework_list, fw1_dict):
    implemented_ETs = find_implemented_ETs(framework_list)
    fw1_controls = control_implemented_status(implemented_ETs, fw1_dict)
    collected_vals = [len(fw1_controls[0])]
    partial_vals = [len(fw1_controls[1])]
    outstanding_vals = [len(fw1_controls[2])]

    collected_and_partial = []
    for collected_val, partial_val in zip(collected_vals, partial_vals):
        collected_and_partial.append(collected_val + partial_val)

    totals = []
    for value, outstanding_val in zip(collected_and_partial, outstanding_vals):
        totals.append(value + outstanding_val)

    ind = np.arange(1)    # the x locations for the groups
    width = .5       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar([1], collected_vals, width, align='center') # [1] is used so that the bar isn't so fat
    p2 = plt.bar([1], partial_vals, width,
                 bottom=collected_vals, color='#f59542', align='center')
    p3 = plt.bar([1], outstanding_vals, width,
              bottom=collected_and_partial, color='#f5424e', align='center')

    implemented_framework_names = ""
    for f in framework_list:
        implemented_framework_names += " " + f['label']

    plt.title('Control status after implementing {0}'.format(implemented_framework_names))
    plt.ylabel('Number of controls')
    plt.xticks(np.arange(3), ["",fw1_dict['label'],""])
    plt.yticks(np.arange(0, max(totals)+50, 10))
    plt.legend((p1[0], p2[0], p3[0]), ["Collected", "Partially Collected", "Outstanding"],
        loc='upper center', ncol=3)
    plt.subplots_adjust(left=0.05, right=0.95) # widen plot so legend fits
    plt.savefig(fw1_dict["label"].replace(" ", "_") + "_Graph.png")
    plt.clf()
    # plt.show()


def manage_header(header):
    if len(header) < 6:
        print("Csv not in expected form, expected at least 6 columns, only found {0}. See README for more detail".
            format(len(header)))
        sys.exit()

    return header[4:] # These are the names of the included frameworks


# Assumes group_codes are separated by a '\n'
def contains_TSC(group_codes, check_code):
    if check_code == "": # If no code, then just accept it
        return True
    codes = group_codes.split("\n")
    if check_code in codes:
        return True
    return False


def main():
    framework_dicts = create_dict_of_frameworks('controls_export.csv')
    fill_frameworks_with_ets('TugbotLogic-Evidence-Tasks.csv', framework_dicts)

    # Parse Command-line Args
    parser = argparse.ArgumentParser(description='Compare an implemented framework with 1 or more investigated frameworks.')
    parser.add_argument('-i', '--implemented', default="SOC 2")
    parser.add_argument('-v', '--investigating', nargs='+', default=["ISO 27001:2013"])
    args = parser.parse_args()

    ### Implemented Framework
    implemented_name = args.implemented


    investigating_names = args.investigating

    print "Implemented Framework: " + implemented_name
    print "Investigating Frameworks... \n"

    try:
        ### Implemented Framework
        implemented_framework = framework_dicts[args.implemented]
        implemented_framework['label'] = args.implemented

        ### For each framework to investigate
        for framework_name in args.investigating:
            print(framework_name)
            framework_dicts[framework_name]['label'] = framework_name
            compare_framework_ETs([implemented_framework], framework_dicts[framework_name])
            single_stacked_bar([implemented_framework], framework_dicts[framework_name])
            print "\n"
    except KeyError:
        sys.exit("Implemented Framework {} Does Not Exist".format(implemented_name))



if __name__ == "__main__":
    main()
