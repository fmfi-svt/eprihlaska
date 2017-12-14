import re
from wtforms import validators


class BirthNo(object):
    def __init__(self, birth_no=-1, message=None):
        self.birth_no = birth_no
        if not message:
            message = u'Zadali ste nesrávne rodné číslo.'
        self.message = message

    def __call__(self, form, field):
        # check if birth_no is 12345678/1234
        birth_no_regex = re.compile(r'(\d\d\d\d\d\d)/(\d\d\d\d)')
        mo = birth_no_regex.search(field.data)
        try:
            mo.group(0)
        except AttributeError:
            raise validators.ValidationError(self.message)

        date_pattern = re.compile(r'[0-9][0-9][0156][0-9][0-3][0-9]')
        if date_pattern.search(mo.group(1)) is None:
            raise validators.ValidationError(self.message)

        # check if 123456781234 % 11 == 0
        birth_no = int(mo.group(1) + mo.group(2))
        if birth_no % 11 != 0:
            raise validators.ValidationError(self.message)
