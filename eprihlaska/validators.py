import re
import datetime
from .models import User
from wtforms import validators
import operator


class BirthNoValidator(object):
    def __init__(self, birth_no=-1, empty_msg=None, message=None, form_err=None, mod_err=None,
                 conditional_field=None, conditional_field_vals=None):
        self.birth_no = birth_no
        self.mod_err = mod_err
        self.form_err = form_err

        if not empty_msg:
            empty_msg = 'Prosím, zadajte svoje rodné číslo.'
        self.empty_msg = empty_msg

        if not message:
            message = 'Zadali ste nesprávne rodné číslo.'
        self.message = message

        if not form_err:
            form_err = 'Správny formát je RRMMDD/CCCC.'
        self.form_err = form_err

        if not mod_err:
            mod_err = 'Vaše rodné číslo nie je deliteľné číslom 11.'
        self.mod_err = mod_err

        self.conditional_field = conditional_field
        self.conditional_field_vals = []
        if conditional_field_vals is not []:
            self.conditional_field_vals = conditional_field_vals


    def __call__(self, form, field):
        bno_reg = re.compile(r'^(([0-9][0-9])(([0156])([0-9]))([0-3][0-9]))/(\d\d\d\d)$')
        mo = bno_reg.search(field.data)

        # If the `conditional_field` has been set, only run the validation if
        # the value of the `conditional_field` is among those passed to the
        # validator via `conditional_field_vals`. Otherwise the validation
        # is not conducted.
        if self.conditional_field is not None:
            conditional_field = form[self.conditional_field]
            if conditional_field.data not in self.conditional_field_vals:
                if not field.data:
                    return

        if not field.data:
            raise(validators.ValidationError(self.empty_msg))

        try:
            mo.group(0)
        except AttributeError:
            raise validators.ValidationError(self.message + ' ' + self.form_err)

        birth_no = int(mo.group(1) + mo.group(7))
        if birth_no % 11 != 0:
            raise validators.ValidationError(self.message + ' ' + self.mod_err)

        year = mo.group(2)
        month = mo.group(3)
        day = mo.group(6)
        if mo.group(4) in ['5', '6']:
            month = '{}{}'.format(int(mo.group(4))-5, mo.group(5))

        try:
            date = '{}.{}.{}'.format(day, month, year)
            datetime.datetime.strptime(date, '%d.%m.%y')
        except ValueError:
            raise validators.ValidationError(self.message)


class DateValidator:
    def __init__(self, date=None, empty_msg=None, message=None, val_err_msg=None):
        self.date = date

        if not empty_msg:
            empty_msg = 'Prosím, zadajte svoj dátum narodenia.'
        self.empty_msg = empty_msg

        if not message:
            message = 'Správny formát je DD.MM.RRRR'
        self.message = message

        if not val_err_msg:
            val_err_msg = 'Neexistujúci dátum.'
        self.val_err_msg = val_err_msg

    def __call__(self, form, field):
        date_reg = re.compile(r'^(\d?\d)\.(\d?\d)\.(\d\d\d\d)$')
        mo = date_reg.search(field.data)

        if not field.data:
            raise validators.ValidationError(self.empty_msg)

        try:
            mo.group(0)
        except AttributeError:
            raise validators.ValidationError(self.message)

        try:
            datetime.datetime.strptime(mo.group(0), '%d.%m.%Y')
        except ValueError:
            raise validators.ValidationError(self.val_err_msg)


class EmailDuplicateValidator:
    def __init__(self, message=None):
        if not message:
            message = 'Zadaný email už bol zaregistrovaný.'
        self.message = message

    def __call__(self, form, field):
        user = User.query.filter_by(email=field.data).first()

        if user:
            raise validators.ValidationError(self.message)

class CityInSKValidator:
    def __init__(self, unacceptable_value, country_field, country_field_value,
                 message=None):
        if not message:
            message = 'Vyberte, prosím, mesto alebo obec v SR.'
        self.message = message
        self.country_field = country_field
        self.country_field_value = country_field_value
        self.unacceptable_value = unacceptable_value

    def __call__(self, form, field):
        country_field = form[self.country_field]

        if country_field.data == self.country_field_value and \
           field.data == self.unacceptable_value:
            raise validators.ValidationError(self.message)

class IfStreetThenCity:
    '''
    If street is filled in, so should be the city.
    '''
    def __init__(self, unacceptable_value, street_field, country_field,
                 country_field_value, message=None, country_negated=False):
        if not message:
            message = 'Vyberte, prosím, mesto alebo obec v SR.'

        self.message = message
        self.country_field = country_field
        self.country_field_value = country_field_value
        self.unacceptable_value = unacceptable_value
        self.street_field = street_field

        self.country_op = operator.eq
        if country_negated:
            self.country_op = operator.ne

    def __call__(self, form, field):
        country_field = form[self.country_field]
        street_field_data = form[self.street_field].data

        if self.country_op(country_field.data, self.country_field_value) and \
           field.data == self.unacceptable_value and \
           street_field_data:
            raise validators.ValidationError(self.message)
