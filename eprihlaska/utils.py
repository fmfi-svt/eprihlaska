import csv

def choices_from_csv(csv_file, keys, delimiter=',', fmt=None):
    reader = csv.DictReader(open(csv_file, 'r', encoding='utf-8'),
                            delimiter=delimiter)
    choices = []
    for line in reader:
        choice = [v for k, v in line.items() if k in keys]
        if fmt:
            choice = [line[keys[0]]]
            choice.append(fmt.format(*line.values()))
        choices.append(tuple(choice))
    return choices
