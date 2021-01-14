# Used to examine relationships between
# Made by Lucas Ramos-Strankman for TugboatLogic
# Jan 2021

import csv
import matplotlib.pyplot as plt
import numpy as np
import sys

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


def add_to_framework_dict(ET_id, control, framework):
    if control != "":
        if control in framework:
            ET_list = framework.get(control)
            ET_list.append(ET_id)
            framework[control] = ET_list
        else:
            framework[control] = [ET_id]


def get_framework_ETs(fw1, fw2):
    fw1_ET_list = set()
    for control, control_ET_list in fw1.iteritems():
        for ET_id in control_ET_list:
            fw1_ET_list.add(ET_id)

    completed = []
    partial = []
    not_done = []
    for control, control_ET_list in fw2.iteritems():
        if control == 'label': # ignores the framework name that is added to the dictionary
            continue
        if all(ET_id in fw1_ET_list for ET_id in control_ET_list):
            completed.append(control)
        elif any(ET_id in fw1_ET_list for ET_id in control_ET_list):
            partial.append(control)
        else:
            not_done.append(control)
    return len(completed), len(partial), len(not_done)


def compare_framework_ETs(fw1, fw2):
    completed, partial, not_done = get_framework_ETs(fw1, fw2)
    print("Completed controls: {0}".format(completed))
    print("Partially Completed controls: {0}".format(partial))
    print("Controls with unique ETs: {0}".format(not_done))


def create_stacked_bar(fw1_dict, fw2_dict):
    fw1_values, fw2_values = get_framework_ETs(fw1_dict, fw2_dict), get_framework_ETs(fw2_dict,fw1_dict)
    completed_vals = [fw1_values[0], fw2_values[0]]
    partial_vals = [fw1_values[1], fw2_values[1]]
    not_done_vals = [fw1_values[2], fw2_values[2]]

    completed_and_partial = []
    for completed_val, partial_val in zip(completed_vals, partial_vals):
        completed_and_partial.append(completed_val + partial_val)

    totals = []
    for value, not_done_val in zip(completed_and_partial, not_done_vals):
        totals.append(value + not_done_val)
    N = 2

    ind = np.arange(N)    # the x locations for the groups
    width = 0.3       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, completed_vals, width, align='center')
    p2 = plt.bar(ind, partial_vals, width,
                 bottom=completed_vals, color='#f59542', align='center')
    p3 = plt.bar(ind, not_done_vals, width,
              bottom=completed_and_partial, color='#f5424e', align='center')

    plt.ylabel('Number of controls')
    plt.title('Collected controls by framework')

    plt.xticks(ind, ['{0} to {1}'.format(fw1_dict.get('label'),fw2_dict.get('label')), '{0} to {1}'.format(fw1_dict.get('label'), fw2_dict.get('label')) ])
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



def main():
    file = "mycsv2.csv"
    data = parse_csv(file)

    framework_labels = manage_header(data.pop(0)) # Popped so the header row is removed

    fw_dicts = []
    for i in range(len(framework_labels)):
        new_framework_dict = {'label':framework_labels[i]}
        fw_dicts.append(new_framework_dict)
        for row in data:
            ET_id = row[0]
            control = row[4+i]
            add_to_framework_dict(ET_id, control, new_framework_dict)


    print("~~~~~~~~~~~~")
    print("{0} -> {1}".format(framework_labels[0], framework_labels[1]))
    compare_framework_ETs(fw_dicts[0], fw_dicts[1])
    print("~~~~~~~~~~~~")
    print("{0} -> {1}".format(framework_labels[1], framework_labels[0]))
    compare_framework_ETs(fw_dicts[1], fw_dicts[0])
    create_stacked_bar(fw_dicts[0], fw_dicts[1])


if __name__ == "__main__":
    main()
