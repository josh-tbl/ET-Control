# Used to examine relationships between
# Made by Lucas Ramos-Strankman for TugboatLogic
# Jan 2021

import csv
import matplotlib.pyplot as plt
import numpy as np


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


def create_visuals(SOC_values, ISO_values):
    labels = ['SOC', 'ISO']
    completed_vals = [SOC_values[0], ISO_values[0]]
    partial_vals = [SOC_values[1], ISO_values[1]]
    not_done_vals = [SOC_values[2], ISO_values[2]]

    completed_and_partial = []
    for completed_val, partial_val in zip(completed_vals, partial_vals):
        completed_and_partial.append(completed_val + partial_val)

    totals = []
    for value, not_done_val in zip(completed_and_partial, not_done_vals):
        totals.append(value + not_done_val)
    N = len(labels)

    ind = np.arange(N)    # the x locations for the groups
    width = 0.3       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, completed_vals, width, align='center')
    p2 = plt.bar(ind, partial_vals, width,
                 bottom=completed_vals, color='#f59542', align='center')
    p3 = plt.bar(ind, not_done_vals, width,
              bottom=completed_and_partial, color='#f5424e', align='center')

    plt.ylabel('Number of controls')
    plt.title('Collected controls by framework')
    plt.xticks(ind, ['SOC to ISO', 'ISO to SOC'])
    plt.yticks(np.arange(0, max(totals)+50, 10))
    plt.legend((p1[0], p2[0], p3[0]), ["Collected", "Partially Collected", "Outstanding"],
        loc='upper center', ncol=3)

    plt.savefig("figure1.png")
    plt.show()


def main():
    file = "mycsv.csv"
    data = parse_csv(file)

    data.pop(0) # get rid of header
    SOC = {}
    ISO = {}
    for row in data:
        ET_id = row[0]
        SOC_control = row[4]
        ISO_control = row[5]
        add_to_framework_dict(ET_id, SOC_control, SOC)
        add_to_framework_dict(ET_id, ISO_control, ISO)

    print("~~~~~~~~~~~~")
    print("SOC2 -> ISO")
    compare_framework_ETs(SOC, ISO)
    print("~~~~~~~~~~~~")
    print("ISO -> SOC2")
    compare_framework_ETs(ISO, SOC)
    create_visuals(get_framework_ETs(SOC, ISO), get_framework_ETs(ISO,SOC))


if __name__ == "__main__":
    main()
