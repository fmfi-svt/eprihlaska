import re
from wtforms import validators


class BirthNo(object):
    def __init__(self, birth_no=-1, message=None):
        self.birth_no = birth_no
        if not message:
            message = u'Zadali ste nesprávne rodné číslo.'
        self.message = message

    def __call__(self, form, field):
        bad_form_err = 'Správny formát je 890101/1234.'
        mod_el_err = 'Vaše rodné číslo nie je deliteľné číslom 11.'

        birth_no_regex = re.compile(r'^(\d\d\d\d\d\d)/(\d\d\d\d)$')
        mo = birth_no_regex.search(field.data)

        try:
            mo.group(0)
        except AttributeError:
            raise validators.ValidationError(self.message + ' ' + bad_form_err)

        date_pattern = re.compile(r'[0-9][0-9][0156][0-9][0-3][0-9]')
        if date_pattern.search(mo.group(1)) is None:
            raise validators.ValidationError(self.message)

        birth_no = int(mo.group(1) + mo.group(2))
        if birth_no % 11 != 0:
            raise validators.ValidationError(self.message + ' ' + mod_el_err)
