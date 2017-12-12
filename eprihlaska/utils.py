import csv

def choices_from_csv(csv_file, keys, delimiter=',', fmt=None):
    reader = csv.DictReader(open(csv_file, 'r', encoding='utf-8'),
                            delimiter=delimiter)
    choices = []
    for line in reader:
        choice = [line[k] for k in reader.fieldnames if k in keys]
        if fmt:
            choice = [line[keys[0]]]
            vals = [line[f] for f in reader.fieldnames]
            choice.append(fmt.format(*vals))
        choices.append(tuple(choice))
    return choices
