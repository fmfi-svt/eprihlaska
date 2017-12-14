import re
from wtforms import validators


class BirthNoValidator(object):
    def __init__(self, birth_no=-1, message=None):
        self.birth_no = birth_no
        if not message:
            message = 'Zadali ste nesprávne rodné číslo.'
        self.message = message

    def __call__(self, form, field):
        bad_form_err = 'Správny formát je RRMMDD/CCCC.'
        mod_el_err = 'Vaše rodné číslo nie je deliteľné číslom 11.'

        bno_reg = re.compile(r'^([0-9][0-9][0156][0-9][0-3][0-9])/(\d\d\d\d)$')
        mo = bno_reg.search(field.data)

        try:
            mo.group(0)
        except AttributeError:
            raise validators.ValidationError(self.message + ' ' + bad_form_err)

        birth_no = int(mo.group(1) + mo.group(2))
        print(birth_no, birth_no % 11)
        if birth_no % 11 != 0:
            raise validators.ValidationError(self.message + ' ' + mod_el_err)
