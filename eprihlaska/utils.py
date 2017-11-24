import csv

def choices_from_csv(csv_file, keys, delimiter=';'):
    reader = csv.DictReader(open(csv_file, 'r'),
                            delimiter=delimiter)
    choices = []
    for line in reader:
        choice = [v for k, v in line.items() if k in keys]
        choices.append(tuple(choice))
    return choices
