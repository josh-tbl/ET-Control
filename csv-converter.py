# Used to extract info from some csvs n stuff
# Made by Lucas Ramos-Strankman for TugboatLogic
# Jan 2021

import csv

# load csv
# Strip into Evidence ID, SOC 2, and ISO columns
# Make Dictionaries for each framework, Dict {control -> (EIDs)}


# NOTE:  some may be duplicates.
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
    return completed, partial, not_done


def compare_framework_ETs(fw1, fw2):
    completed, partial, not_done = get_framework_ETs(fw1, fw2)
    print("Completed controls: {0}".format(len(completed)))
    print("Partially Completed controls: {0}".format(len(partial)))
    print("Controls with no ETs: {0}".format(len(not_done)))



def main():
    file = "testcsv1.csv"
    info = parse_csv(file)

    info.pop(0) # get rid of header
    SOC = {}
    ISO = {}
    for row in info:
        ET_id = row[0]
        SOC_control = row[4]
        ISO_control = row[5]
        add_to_framework_dict(ET_id, SOC_control, SOC)
        add_to_framework_dict(ET_id, ISO_control, ISO)

    # someset = set()
    # for i,v in ISO.iteritems():
    #     someset.add(i)
    #     # if len(v) > 1:
    #     print(i)
    #     # print(v)
    # print(len(someset))

    print("~~~~~~~~~~~~")
    print("SOC2 -> ISO")
    compare_framework_ETs(SOC, ISO)
    print("~~~~~~~~~~~~")
    print("ISO -> SOC2")
    compare_framework_ETs(ISO, SOC)

if __name__ == "__main__":
    main()
# Find duplicates
# for i,v in SOC.iteritems():
#     if len(v) > 1:
#         print(i)
#         print(v)

# print(SOC)
