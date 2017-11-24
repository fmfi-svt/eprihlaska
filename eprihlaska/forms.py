from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, RadioField, SubmitField,
                     validators, SelectField, FormField, SelectMultipleField,
                     DateField)

from .utils import choices_from_csv

class FatherNameForm(FlaskForm):
    name = StringField('Meno otca')
    surname = StringField('Priezvisko otca')
    born_with_surname = StringField('Rodné priezvisko otca')

class MotherNameForm(FlaskForm):
    name = StringField('Meno matky')
    surname = StringField('Priezvisko matky')
    born_with_surname = StringField('Rodné priezvisko matky')


class BasicPersonalDataForm(FlaskForm):
    nationality = SelectField('Občianstvo',
                              choices=choices_from_csv('eprihlaska/data/krajiny-osn.csv',
                                                       ['kód', 'názov']),
                              validators=[validators.DataRequired()])

    name = StringField('Meno', validators=[validators.DataRequired()])
    surname = StringField('Priezvisko', validators=[validators.DataRequired()])
    born_with_surname = StringField('Rodné priezvisko')

    rodinny_stav = SelectField('Rodinný stav',
                               choices=choices_from_csv('eprihlaska/data/rodinne-stavy.csv',
                                                       ['kód', 'názov']))
    sex = SelectField(label='Pohlavie',
                     choices=[('male', 'muž'), ('female', 'žena')],
                     validators=[validators.DataRequired()])
    submit = SubmitField()

class MoreDetailPersonalDataForm(FlaskForm):
    birth_no = StringField('Rodné číslo')
    date_of_birth = DateField('Dátum narodenia',
                              validators=[validators.DataRequired()],
                              format='%d.%m.%Y')
    place_of_birth = SelectField('Miesto narodenia',
                                 choices=choices_from_csv('eprihlaska/data/obce.csv',
                                                       ['kód', 'názov']),
                                 validators=[validators.DataRequired()])

    email = StringField('Email', validators=[validators.DataRequired(),
                                             validators.Email()])
    phone = StringField('Telefónny kontakt', validators=[validators.DataRequired()])

class FurtherPersonalDataForm(FlaskForm):
    basic_personal_data = FormField(MoreDetailPersonalDataForm, label='Ďalšie osobné údaje')
    father_name = FormField(FatherNameForm, label='Informácie o otcovi')
    mother_name = FormField(MotherNameForm, label='Informácie o matke')

    submit = SubmitField()


class StudyProgrammeForm(FlaskForm):
    study_programme = SelectMultipleField(label='Študijný program',
                                          choices=[('inf', 'Informatika'),
                                                   ('ain', 'Aplikovaná informatika'),
                                                   ('bin', 'Bioinformatika'),
                                                   ('efm', 'Ekonomická a finančná matematika')])
    submit = SubmitField()


class AddressSK(FlaskForm):
    street = StringField('Ulica', validators=[validators.DataRequired()])
    street_no = StringField('Číslo', validators=[validators.DataRequired()])
    city = StringField('Mesto', validators=[validators.DataRequired()])
    psc = StringField('PSČ', validators=[validators.DataRequired()])

class AddressSK(FlaskForm):
    street = StringField('Ulica', validators=[validators.DataRequired()])
    street_no = StringField('Číslo', validators=[validators.DataRequired()])
    city = SelectField('Mesto',
                       choices=choices_from_csv('eprihlaska/data/obce.csv',
                                                ['kód', 'názov']),
                       validators=[validators.DataRequired()])
    psc = SelectField('PSČ',
                      choices=choices_from_csv('eprihlaska/data/psc-obci-sr.csv',
                                                ['Kód obce', 'PSČ']),
                      validators=[validators.DataRequired()])

class AddressForm(FlaskForm):
    address = FormField(AddressSK, label='Adresa trvalého bydliska')
    corresponding_address = FormField(AddressSK,
                                      label='Korešpondenčnná adresa')
    submit = SubmitField()



