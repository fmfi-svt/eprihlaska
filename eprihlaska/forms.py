from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, RadioField, SubmitField,
                     validators, SelectField, FormField, SelectMultipleField,
                     DateField, BooleanField)

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
                                          choices=[('MAT', 'Matematika'),
                                                   ('PMA', 'Poistná matematika'),
                                                   ('EFM', 'Ekonomická a finančná matematika'),
                                                   ('MMN', 'Manažérska matematika'),
                                                   ('FYZ', 'Fyzika'),
                                                   ('BMF', 'Biomedicínska fyzika'),
                                                   ('OZE', 'Obnoviteľné zdroje energie a environmentálna fyzika'),
                                                   ('INF', 'Informatika'),
                                                   ('AIN', 'Aplikovaná informatika'),
                                                   ('BIN', 'Bioinformatika'),
                                                   ('upMAFY', 'Učiteľstvo matematiky a fyziky'),
                                                   ('upMAIN', 'Učiteľstvo matematiky a informatiky'),
                                                   ('upFYIN', 'učiteľstvo fyziky a informatiky'),
                                                   ('upMATV', 'učiteľstvo matematiky a telesnej výchovy'),
                                                   ('upMADG', 'učiteľstvo matematiky a deskriptívnej geometrie'),
                                                   ('upINBI', 'učiteľstvo informatiky a biológie'),
                                                   ('upINAN', 'učiteľstvo informatiky a anglického jazyka a literatúry')],
                                            description='Vyberte si aspoň jeden a najviac tri študijné programy')
    matura_year = StringField('Rok maturity', validators=[validators.DataRequired()])
    dean_invitation_letter = BooleanField('Dostal som list od dekana')
    dean_invitation_letter_no = StringField('Číslo listu od dekana',
                                            description='Prosím, vyplňte číslo listu od dekana, ktorý ste dostali')
    submit = SubmitField()


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



