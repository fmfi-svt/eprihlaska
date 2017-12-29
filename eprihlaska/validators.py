import re
import datetime
from wtforms import validators


class BirthNoValidator(object):
    def __init__(self, birth_no=-1, message=None, form_err=None, mod_err=None):
        self.birth_no = birth_no
        self.mod_err = mod_err
        self.form_err = form_err

        if not message:
            message = 'Zadali ste nesprávne rodné číslo.'
        self.message = message

        if not form_err:
            form_err = 'Správny formát je RRMMDD/CCCC.'
        self.form_err = form_err

        if not mod_err:
            mod_err = 'Vaše rodné číslo nie je deliteľné číslom 11.'
        self.mod_err = mod_err

    def __call__(self, form, field):
        bno_reg = re.compile(r'^([0-9][0-9][0156][0-9][0-3][0-9])/(\d\d\d\d)$')
        mo = bno_reg.search(field.data)

        # If someone doesn't have a birth number, empty field is also accepted.
        if field.data:
            try:
                mo.group(0)
            except AttributeError:
                raise validators.ValidationError(self.message + ' ' + self.form_err)

            birth_no = int(mo.group(1) + mo.group(2))
            if birth_no % 11 != 0:
                raise validators.ValidationError(self.message + ' ' + self.mod_err)


class DateValidator:
    def __init__(self, date=None, message=None, val_err_msg=None):
        self.date = date

        if not message:
            message = 'Správny formát je DD.MM.RRRR'
        self.message = message

        if not val_err_msg:
            val_err_msg = 'Neexistujúci dátum.'
        self.val_err_msg = val_err_msg

    def __call__(self, form, field):
        date_reg = re.compile(r'^(\d\d)\.(\d\d)\.(\d\d\d\d)$')
        mo = date_reg.search(field.data)

        try:
            mo.group(0)
        except AttributeError:
            raise validators.ValidationError(self.message)

        try:
            datetime.datetime.strptime(mo.group(0), '%d.%m.%Y')
        except ValueError:
            raise ValueError(self.val_err_msg)
