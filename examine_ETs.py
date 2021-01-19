# Used to examine shared ETs between frameworks
# Made by Lucas Ramos-Strankman for TugboatLogic
# Jan 2021

# Code was designed to be used from the commandline
# Developed for Python 2.7 as that comes stock in Mac

# Overview of how it works:
# After reading the csv in, we create dictionaries for each framework
# The control name is used as a key, and leads to a list of evidence task ids
# Each control is then mapped to a list of ET ids that it requires
# Using these dictionaries, we can make lists of "implemented" ETs
# and see how many controls of another framework are satisfied by this list
# Finally, we can plot this information using matplotlib

import csv
import matplotlib.pyplot as plt
import numpy as np
import sys


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
    print("collected controls: {0}".format(len(collected)))
    print("Partially collected controls: {0}".format(len(partial)))
    print("Controls with unique ETs: {0}".format(len(outstanding)))


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
    width = 0.1       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, collected_vals, width, align='center')
    p2 = plt.bar(ind, partial_vals, width,
                 bottom=collected_vals, color='#f59542', align='center')
    p3 = plt.bar(ind, outstanding_vals, width,
              bottom=collected_and_partial, color='#f5424e', align='center')

    plt.ylabel('Number of controls')
    plt.title('Collected controls by framework')
    plt.xticks(ind, ['{0}'.format(fw1_dict.get('label'))])
    plt.yticks(np.arange(0, max(totals)+50, 10))
    plt.legend((p1[0], p2[0], p3[0]), ["Collected", "Partially Collected", "Outstanding"],
        loc='upper center', ncol=3)
    plt.savefig("figure1.png")
    plt.show()


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
    file = "csv_ET.csv"
    data = parse_csv(file)
    framework_labels = manage_header(data.pop(0)) # Popped so the header row is removed

    fw_dicts = []
    for i in range(len(framework_labels)):
        new_framework_dict = {'label':framework_labels[i]}
        fw_dicts.append(new_framework_dict)
        for row in data:
            if contains_TSC(row[3], ""): # Used to filter by TSC Code, "" is no filter
                ET_id = row[0]
                control = row[4+i]
                add_to_framework_dict(ET_id, control, new_framework_dict)

    print("~~~~~~~~~~~~")
    print("{0} -> {1}".format(framework_labels[0], framework_labels[1]))
    compare_framework_ETs([fw_dicts[0]], fw_dicts[1])
    print("~~~~~~~~~~~~")
    print("{0} -> {1}".format(framework_labels[1], framework_labels[0]))
    compare_framework_ETs([fw_dicts[1]], fw_dicts[0])
    dual_stacked_bar(fw_dicts[0], fw_dicts[1])
    # single_stacked_bar([fw_dicts[0]], fw_dicts[1]) # Examines ISO assuming SOC is implemented


if __name__ == "__main__":
    main()
