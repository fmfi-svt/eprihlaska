from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, RadioField, SubmitField,
                     validators, SelectField, FormField, SelectMultipleField,
                     DateField, FieldList, IntegerField, HiddenField)

from .validators import BirthNoValidator
from .utils import choices_from_csv
from . import consts as c
import os
import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATE = datetime.datetime.now() - datetime.timedelta(days=17 * 365)

class FatherNameForm(FlaskForm):
    name = StringField(label=c.FATHER_NAME)
    surname = StringField(label=c.FATHER_SURNAME)
    born_with_surname = StringField(label=c.FATHER_BORNWITH_SURNAME)

class MotherNameForm(FlaskForm):
    name = StringField(label=c.MOTHER_NAME)
    surname = StringField(label=c.MOTHER_SURNAME)
    born_with_surname = StringField(label=c.MOTHER_BORNWITH_SURNAME)


class BasicPersonalDataForm(FlaskForm):
    nationality = SelectField(label=c.NATIONALITY,
                              choices=choices_from_csv(DIR + '/data/staty.csv',
                                                       ['id', 'Štát']),
                              validators=[validators.DataRequired()],
                              default='703')

    name = StringField(label=c.NAME,
                       validators=[validators.DataRequired()])
    surname = StringField(label=c.SURNAME,
                          validators=[validators.DataRequired()])
    born_with_surname = StringField(c.BORNWITH_SURNAME)

    marital_status = SelectField(label=c.MARITAL_STATUS,
                               choices=choices_from_csv(DIR + '/data/rodinne-stavy.csv',
                                                       ['id', 'Rodinný stav']),
                               default='1')
    sex = SelectField(label=c.SEX,
                      choices=[('male', c.MALE),
                               ('female', c.FEMALE)],
                      validators=[validators.DataRequired()])
    personal_info = HiddenField()
    submit = SubmitField()

class ePrihlaskaDateField(DateField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d',
                 **kwargs):
        super(ePrihlaskaDateField, self).__init__(label, validators, format,
                                                  **kwargs)

    def process_formdata(self, valuelist):
        # Use DateField's parent's (DateTimeField) process_formdata to get
        # datetime.datetime rather than datetime.datetime.date which is
        # dificult to serialize for Flask.
        super(DateField, self).process_formdata(valuelist)

class MoreDetailPersonalDataForm(FlaskForm):
    birth_no = StringField(label=c.BIRTH_NO,
                           validators=[BirthNoValidator()])
    date_of_birth = ePrihlaskaDateField(label=c.BIRTH_DATE,
                                        format='%d.%m.%Y',
                                        default=DEFAULT_DATE)
    country_of_birth = SelectField(label=c.BIRTH_COUNTRY,
                                   choices=choices_from_csv(DIR + '/data/staty.csv',
                                                            ['id', 'Štát']),
                                   default='703')

    place_of_birth = SelectField(label=c.BIRTH_PLACE,
                                 choices=choices_from_csv(DIR + '/data/obce.csv',
                                                          ['id', 'Názov obce'],
                                                          fmt='{2} ({3})'))

    place_of_birth_foreign = StringField(label=c.BIRTH_PLACE_FOREIGN)
    email = StringField(label=c.EMAIL,
                        validators=[validators.DataRequired(),
                                    validators.Email()])
    phone = StringField(label=c.PHONE_CONTACT)

class FurtherPersonalDataForm(FlaskForm):
    basic_personal_data = FormField(MoreDetailPersonalDataForm,
                                    label=c.FURTHER_PERSONAL_DATA)
    father_name = FormField(FatherNameForm, label=c.INFO_FATHER)
    mother_name = FormField(MotherNameForm, label=c.INFO_MATHER)

    further_personal_info = HiddenField()
    submit = SubmitField()


class StudyProgrammeForm(FlaskForm):
    study_programme = SelectMultipleField(label=c.STUDY_PROGRAMME,
                                          choices=c.STUDY_PROGRAMME_CHOICES,
                                          description=c.STUDY_PROGRAMME_DESC)
    matura_year = IntegerField(c.MATURA_YEAR,
                               default=2018,
                               validators=[validators.DataRequired(),
                                           validators.NumberRange(min=1900,
                                                                  max=2018)])
    dean_invitation_letter = BooleanField(label=c.DEAN_INV_LIST_YN)
    dean_invitation_letter_no = StringField(label=c.DEAN_INV_LIST_NO,
                                            description=c.DEAN_INV_LIST_NO_DESC)
    index = HiddenField()
    submit = SubmitField()


class Address(FlaskForm):
    country = SelectField(label=c.ADDRESS_COUNTRY,
                              choices=choices_from_csv(DIR + '/data/staty.csv',
                                                       ['id', 'Štát']),
                              default='703')
    street = StringField(label=c.ADDRESS_STREET)
    street_no = StringField(label=c.ADDRESS_NO)
    city = SelectField(label=c.ADDRESS_CITY,
                       choices=choices_from_csv(DIR + '/data/obce.csv',
                                                ['id', 'Názov obce'],
                                                fmt='{2} ({3})'))
    city_foreign = StringField(label=c.ADDRESS_CITY_FOREIGN)
    postal_no = StringField(label=c.ADDRESS_POSTAL_NO)


class AddressNonRequired(FlaskForm):
    country = SelectField(label=c.ADDRESS_COUNTRY,
                              choices=choices_from_csv(DIR + '/data/staty.csv',
                                                       ['id', 'Štát']),
                              default='703')
    street = StringField(label=c.ADDRESS_STREET)
    street_no = StringField(label=c.ADDRESS_NO)
    city = SelectField(label=c.ADDRESS_CITY,
                       choices=choices_from_csv(DIR + '/data/obce.csv',
                                                ['id', 'Názov obce'],
                                                fmt='{2} ({3})'))
    city_foreign = StringField(label=c.ADDRESS_CITY_FOREIGN)
    postal_no = StringField(label=c.ADDRESS_POSTAL_NO)


class AddressForm(FlaskForm):
    address_form = FormField(Address, label=c.PERMANENT_ADDRESS)
    has_correspondence_address = BooleanField(label=c.HAS_CORRESPONDENCE_ADDRESS)
    correspondence_address = FormField(AddressNonRequired,
                                       label=c.CORRESPONDENCE_ADDRESS)
    address = HiddenField()
    submit = SubmitField()

class StudiesInSRForm(FlaskForm):
    highschool = SelectField(label=c.HIGHSCHOOL,
                             choices=choices_from_csv(DIR + '/data/skoly.csv',
                                                ['St. šk.', 'Obec',
                                                 'Stredná škola',
                                                 'Ulica'],
                                                fmt='{2}, {3}, {4}'))
    study_programme_code = SelectField(label=c.STUDY_PROGRAMME_CODE,
                             default='7902J00',
                             choices=choices_from_csv(DIR + '/data/odbory.csv',
                                                ['Odbor - kod',
                                                 'Odbor stred. školy'],
                                                fmt='{1} - {2}'))

    education_level = SelectField(label=c.HS_EDUCATION_LEVEL,
                             default='J',
                             choices=choices_from_csv(DIR + '/data/vzdelanie.csv',
                                                ['Kód',
                                                 'Skrát. popis'],
                                                fmt='({1}) - {3}'))

class ForeignStudiesForm(FlaskForm):
    finished_highschool = BooleanField(label=c.FOREIGN_FINISHED_HIGHSCHOOL)


class PreviousStudiesForm(FlaskForm):
    has_previously_studied = BooleanField(label=c.HAS_PREVIOUSLY_STUDIED)
    finished_highschool_check = RadioField(label=c.FINISHED_HIGHSCHOOL,
                                     choices=[('SK', c.IN_SR),
                                              ('OUTSIDE', c.OUTSIDE_OF_SR)],
                                     default='SK',
                                     validators=[validators.DataRequired()])
    studies_in_sr = FormField(StudiesInSRForm, label=c.STUDIES_IN_SR)
    foreign_studies = FormField(ForeignStudiesForm, label=c.FOREIGN_STUDIES)
    previous_studies = HiddenField()
    submit = SubmitField()

class CompetitionSuccessFormItem(FlaskForm):
    competition = SelectField(label=c.COMPETITION_NAME,
                              choices=c.COMPETITION_CHOICES)
    year = IntegerField(label=c.COMPETITION_YEAR,
                        validators=[validators.Optional()])
    further_info = StringField(label=c.COMPETITION_FURTHER_INFO,
                               description=c.COMPETITION_FURTHER_INFO_DESC)


class FurtherStudyInfoForm(FlaskForm):
    external_matura_percentile = StringField(label=c.EXTERNAL_MATURA_PERCENTILE)
    scio_percentile = StringField(label=c.SCIO_PERCENTILE)

    matura_mat_grade = IntegerField(label=c.MATURA_MAT_GRADE,
                                    validators=[validators.Optional()])
    matura_fyz_grade = IntegerField(label=c.MATURA_FYZ_GRADE,
                                    validators=[validators.Optional()])
    matura_inf_grade = IntegerField(label=c.MATURA_INF_GRADE,
                                    validators=[validators.Optional()])
    matura_bio_grade = IntegerField(label=c.MATURA_BIO_GRADE,
                                    validators=[validators.Optional()])
    matura_che_grade = IntegerField(label=c.MATURA_CHE_GRADE,
                                    validators=[validators.Optional()])

    will_take_external_mat_matura = BooleanField(label=c.WILL_TAKE_EXT_MAT)
    will_take_scio = BooleanField(label=c.WILL_TAKE_SCIO)

    will_take_mat_matura = BooleanField(label=c.WILL_TAKE_MAT_MATURA)
    will_take_fyz_matura = BooleanField(label=c.WILL_TAKE_FYZ_MATURA)
    will_take_inf_matura = BooleanField(label=c.WILL_TAKE_INF_MATURA)
    will_take_che_matura = BooleanField(label=c.WILL_TAKE_CHE_MATURA)
    will_take_bio_matura = BooleanField(label=c.WILL_TAKE_BIO_MATURA)

class FurtherGradesInfoForm(FlaskForm):
    grade_first_year = IntegerField(c.GRADE_FIRST_YEAR,
                                    validators=[validators.Optional()])
    grade_second_year = IntegerField(c.GRADE_SECOND_YEAR,
                                     validators=[validators.Optional()])
    grade_third_year = IntegerField(c.GRADE_THIRD_YEAR,
                                    validators=[validators.Optional()])

class AdmissionWaversForm(FlaskForm):
    further_study_info = FormField(FurtherStudyInfoForm,
                                   label=c.FURTHER_STUDY_INFO)

    grades_mat = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_MAT)
    grades_fyz = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_FYZ)
    grades_bio = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_BIO)

    competition_1 = FormField(CompetitionSuccessFormItem,
                              label=c.COMPETITION_FIRST)
    competition_2 = FormField(CompetitionSuccessFormItem,
                              label=c.COMPETITION_SECOND)
    competition_3 = FormField(CompetitionSuccessFormItem,
                              label=c.COMPETITION_THIRD)
    admissions_wavers = HiddenField()
    submit = SubmitField()
