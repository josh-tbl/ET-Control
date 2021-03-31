# Used to examine shared ETs between frameworks
# Made by Lucas Ramos-Strankman for TugboatLogic
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


def output_to_file(collected, partial, outstanding):
    file = open("Control_breakdown.txt", "w")

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
    output_to_file(collected, partial, outstanding) #outputs the results to a txt file
    col_num = len(collected)
    par_num = len(partial)
    out_num = len(outstanding)
    all_num = col_num + par_num + out_num
    print("Collected controls: {0}".format(col_num))
    print("Partially collected controls: {0}".format(par_num))
    print("Controls with unique ETs: {0}".format(out_num))
    print("Collected controls/rest = {}/{} = {:.2f}% ".format(col_num, all_num, float(col_num)/all_num*100 ))


def dual_stacked_bar(fw1_dict, fw2_dict):
    fw1_implemented_ETs = find_implemented_ETs([fw1_dict])
    fw2_implemented_ETs = find_implemented_ETs([fw2_dict])

    fw1_values = control_implemented_status(fw1_implemented_ETs, fw2_dict)
    fw2_values = control_implemented_status(fw2_implemented_ETs, fw1_dict)
    collected_vals = [len(fw1_values[0]), len(fw2_values[0])]
    partial_vals = [len(fw1_values[1]), len(fw2_values[1])]
    outstanding_vals = [len(fw1_values[2]), len(fw2_values[2])]

    collected_and_partial = []
    for collected_val, partial_val in zip(collected_vals, partial_vals):
        collected_and_partial.append(collected_val + partial_val)

    totals = []
    for value, outstanding_val in zip(collected_and_partial, outstanding_vals):
        totals.append(value + outstanding_val)

    N = 2
    ind = np.arange(N)    # the x locations for the groups
    width = 0.3

    p1 = plt.bar(ind, collected_vals, width, align='center')
    p2 = plt.bar(ind, partial_vals, width,
                 bottom=collected_vals, color='#f59542', align='center')
    p3 = plt.bar(ind, outstanding_vals, width,
              bottom=collected_and_partial, color='#f5424e', align='center')

    fw1_label = fw1_dict.get('label')
    fw2_label = fw2_dict.get('label')
    plt.ylabel('Number of controls')
    plt.title('Collected controls by framework')
    plt.xticks(ind, ['{0} to {1}'.format(fw1_label, fw2_label),
        '{0} to {1}'.format(fw2_label, fw1_label) ])
    plt.yticks(np.arange(0, max(totals)+50, 10))
    plt.legend((p1[0], p2[0], p3[0]), ["Collected", "Partially Collected", "Outstanding"],
        loc='upper center', ncol=3)

    plt.savefig("figure1.png")
    plt.show()


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
    plt.savefig("figure1.png")
    # plt.show()


# Assumes group_codes are separated by a '\n'
def contains_TSC(group_codes, check_code):
    if check_code == "": # If no code, then just accept it
        return True
    codes = group_codes.split("\n")
    if check_code in codes:
        return True
    return False


def main():
    f = create_dict_of_frameworks('controls_export.csv')
    fill_frameworks_with_ets('TugbotLogic-Evidence-Tasks.csv', f)

    ### implemented
    label1 = "NIST CSF"
    ## investigating
    label2 = "ISO 27001:2013"

    x = f[label1]
    s = f[label2]

    x['label'] = label1
    s['label'] = label2

    frameworks_list = []
    frameworks_list.append(x)

    compare_framework_ETs(frameworks_list, s)
    single_stacked_bar(frameworks_list, s)





if __name__ == "__main__":
    main()
