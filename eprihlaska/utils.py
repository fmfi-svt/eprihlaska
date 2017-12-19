import csv
import locale
import re

def choices_from_csv(csv_file, keys, delimiter=',', fmt=None, sortby=None,
                     prepend=None, post_fmt=None):
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

    if post_fmt:
        choices = list(map(lambda x: [x[0], post_fmt(x[1])], choices))
    if sortby:
        choices = sorted(choices, key=lambda x: locale.strxfrm(x[sortby]))
    if prepend:
        prepends = []
        new_choices = []
        for c in choices:
            if c[0] in prepend:
                prepends.append(c)
            else:
                new_choices.append(c)

        for p in prepends:
            new_choices.insert(0, p)
        choices = new_choices
    return choices

def city_formatter(x):
    return re.sub(r'^([^- ,]+)-[^,]+', r'\1', x)
