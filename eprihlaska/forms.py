from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, BooleanField, RadioField, SubmitField,
                     validators, SelectField, FormField,
                     IntegerField, HiddenField, PasswordField, TextAreaField)

from .validators import (BirthNoValidator, DateValidator,
                         EmailDuplicateValidator, CityInSKValidator,
                         IfStreetThenCity)
from . import consts as c


class FatherNameForm(FlaskForm):
    name = StringField(label=c.FATHER_NAME)
    surname = StringField(label=c.FATHER_SURNAME)
    born_with_surname = StringField(label=c.FATHER_BORNWITH_SURNAME)


class MotherNameForm(FlaskForm):
    name = StringField(label=c.MOTHER_NAME)
    surname = StringField(label=c.MOTHER_SURNAME)
    born_with_surname = StringField(label=c.MOTHER_BORNWITH_SURNAME)


class PersonalDataForm(FlaskForm):
    sex = SelectField(label=c.SEX,
                      choices=c.SEX_CHOICES,
                      validators=[validators.DataRequired()])

    nationality = SelectField(label=c.NATIONALITY,
                              choices=c.COUNTRY_CHOICES,
                              validators=[validators.DataRequired()],
                              default='703')
    birth_no = StringField(label=c.BIRTH_NO,
                           validators=[BirthNoValidator(conditional_field='nationality',
                                                        conditional_field_vals=['703'])],
                           render_kw={"placeholder": 'RRMMDD/CCCC'})
    date_of_birth = StringField(label=c.BIRTH_DATE,
                                validators=[DateValidator()],
                                render_kw={"placeholder": 'DD.MM.RRRR'})

    country_of_birth = SelectField(label=c.BIRTH_COUNTRY,
                                   choices=c.COUNTRY_CHOICES,
                                   default='703')

    place_of_birth = SelectField(label=c.BIRTH_PLACE,
                                 choices=c.CITY_CHOICES,
                                 default='999999',
                                 validators=[CityInSKValidator('999999',
                                                               'country_of_birth',
                                                               '703')])

    place_of_birth_foreign = StringField(label=c.BIRTH_PLACE_FOREIGN)

    marital_status = SelectField(label=c.MARITAL_STATUS,
                                 choices=c.MARITAL_STATUS_CHOICES,
                                 default='1')

    email = StringField(label=c.EMAIL,
                        validators=[validators.DataRequired(),
                                    validators.Email()])
    phone = StringField(label=c.PHONE_CONTACT)

    personal_info = HiddenField()
    submit = SubmitField(label=c.NEXT)



class BasicPersonalDataForm(FlaskForm):
    personal_info_check = BooleanField(label=c.PERSONAL_INFO_CHECK,
                                       validators=[validators.DataRequired()])
    name = StringField(label=c.NAME,
                       validators=[validators.DataRequired()])
    surname = StringField(label=c.SURNAME,
                          validators=[validators.DataRequired()])
    born_with_surname = StringField(c.BORNWITH_SURNAME)

    matura_year = IntegerField(c.MATURA_YEAR,
                               default=c.CURRENT_MATURA_YEAR,
                               validators=[validators.DataRequired(),
                                           validators.NumberRange(min=1900,
                                                                  max=c.CURRENT_MATURA_YEAR)])
    dean_invitation_letter = BooleanField(label=c.DEAN_INV_LIST_YN)
    dean_invitation_letter_no = StringField(label=c.DEAN_INV_LIST_NO,
                                            description=c.DEAN_INV_LIST_NO_DESC)


class SelectStudyProgrammeForm(FlaskForm):
    study_programme_1 = SelectField(label=c.STUDY_PROGRAMME_1,
                                    choices=c.STUDY_PROGRAMME_CHOICES_ACTIVE)
    study_programme_2 = SelectField(label=c.STUDY_PROGRAMME_2,
                                    choices=c.STUDY_PROGRAMME_CHOICES_ACTIVE)
    study_programme_3 = SelectField(label=c.STUDY_PROGRAMME_3,
                                    choices=c.STUDY_PROGRAMME_CHOICES_ACTIVE)


class StudyProgrammeForm(FlaskForm):
    basic_personal_data = FormField(BasicPersonalDataForm,
                                    label=c.BASIC_PERSONAL_DATA)
    study_programme_data = FormField(SelectStudyProgrammeForm,
                                     label=c.STUDY_PROGRAMMES)

    index = HiddenField()
    submit = SubmitField(label=c.NEXT)


class Address(FlaskForm):
    country = SelectField(label=c.ADDRESS_COUNTRY,
                          choices=c.COUNTRY_CHOICES,
                          default='703')
    street = StringField(label=c.ADDRESS_STREET,
                         description=c.ADDRESS_STREET_DESC)
    street_no = StringField(label=c.ADDRESS_NO)
    city = SelectField(label=c.ADDRESS_CITY,
                       choices=c.CITY_CHOICES,
                       default='999999',
                       validators=[IfStreetThenCity(unacceptable_value='999999',
                                                    street_field='street',
                                                    country_field='country',
                                                    country_field_value='703')])
    city_foreign = StringField(label=c.ADDRESS_CITY_FOREIGN,
                               validators=[IfStreetThenCity(unacceptable_value='',
                                                            street_field='street',
                                                            country_field='country',
                                                            country_field_value='703',
                                                            country_negated=True,
                                                            message=c.ADDRESS_CITY_FOREIGN_FILL)])
    postal_no = StringField(label=c.ADDRESS_POSTAL_NO,
                            validators=[validators.Length(max=10)])


class AddressForm(FlaskForm):
    address_form = FormField(Address, label=c.PERMANENT_ADDRESS)
    has_correspondence_address = BooleanField(label=c.HAS_CORRESPONDENCE_ADDRESS)
    correspondence_address = FormField(Address,
                                       label=c.CORRESPONDENCE_ADDRESS)
    address = HiddenField()
    submit = SubmitField(label=c.NEXT)


class StudiesInSRForm(FlaskForm):
    highschool = SelectField(label=c.HIGHSCHOOL,
                             choices=c.HIGHSCHOOL_CHOICES,
                             description=c.HIGHSCHOOL_DESC,
                             default='XXXXXXX')
    study_programme_code = SelectField(label=c.STUDY_PROGRAMME_CODE,
                                       default='7902J00',
                                       description=c.STUDY_PROGRAMME_CODE_DESC,
                                       choices=c.HS_STUDY_PROGRAMME_CHOICES)

    education_level = SelectField(label=c.HS_EDUCATION_LEVEL,
                                  default='J',
                                  choices=c.EDUCATION_LEVEL_CHOICES)


class ForeignStudiesForm(FlaskForm):
    finished_highschool = BooleanField(label=c.FOREIGN_FINISHED_HIGHSCHOOL)


class PreviousStudiesForm(FlaskForm):
    has_previously_studied = BooleanField(label=c.HAS_PREVIOUSLY_STUDIED)
    finished_highschool_check = RadioField(label=c.FINISHED_HIGHSCHOOL,
                                           choices=[('SK', c.IN_SR),
                                                    ('OUTSIDE', c.OUTSIDE_OF_SR)],
                                           default='SK',
                                           validators=[validators.DataRequired()])
    length_of_study = RadioField(label=c.LENGTH_OF_STUDY,
                                 choices=c.LENGTH_OF_STUDY_CHOICES,
                                 default=c.LENGTH_OF_STUDY_DEFAULT,
                                 validators=[validators.DataRequired()])

    studies_in_sr = FormField(StudiesInSRForm, label=c.STUDIES_IN_SR)
    foreign_studies = FormField(ForeignStudiesForm, label=c.FOREIGN_STUDIES)
    previous_studies = HiddenField()
    submit = SubmitField(label=c.NEXT)


class CompetitionSuccessFormItem(FlaskForm):
    competition = SelectField(label=c.COMPETITION_NAME,
                              choices=c.COMPETITION_CHOICES,
                              default='_')
    year = IntegerField(label=c.COMPETITION_YEAR,
                        validators=[validators.Optional(),
                                    validators.NumberRange(min=1990,
                                                           max=c.CURRENT_MATURA_YEAR,
                                                           message=c.YEAR_ERR)])
    further_info = StringField(label=c.COMPETITION_FURTHER_INFO,
                               description=c.COMPETITION_FURTHER_INFO_DESC)


class FurtherStudyInfoForm(FlaskForm):
    g_min = 1
    g_max = 5

    will_take_external_mat_matura = BooleanField(label=c.WILL_TAKE_EXT_MAT)
    will_take_scio = BooleanField(label=c.WILL_TAKE_SCIO)

    will_take_mat_matura = BooleanField(label=c.WILL_TAKE_MAT_MATURA)
    will_take_fyz_matura = BooleanField(label=c.WILL_TAKE_FYZ_MATURA)
    will_take_inf_matura = BooleanField(label=c.WILL_TAKE_INF_MATURA)
    will_take_che_matura = BooleanField(label=c.WILL_TAKE_CHE_MATURA)
    will_take_bio_matura = BooleanField(label=c.WILL_TAKE_BIO_MATURA)

    external_matura_percentile = StringField(label=c.EXTERNAL_MATURA_PERCENTILE)
    scio_percentile = StringField(label=c.SCIO_PERCENTILE)
    scio_date = StringField(label=c.SCIO_DATE)
    scio_cert_no = StringField(label=c.SCIO_CERT_NO,
                               description=c.SCIO_CERT_NO_DESC)

    matura_mat_grade = IntegerField(label=c.MATURA_MAT_GRADE,
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])
    matura_fyz_grade = IntegerField(label=c.MATURA_FYZ_GRADE,
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])
    matura_inf_grade = IntegerField(label=c.MATURA_INF_GRADE,
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])
    matura_bio_grade = IntegerField(label=c.MATURA_BIO_GRADE,
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])
    matura_che_grade = IntegerField(label=c.MATURA_CHE_GRADE,
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])


class FurtherGradesInfoForm(FlaskForm):
    g_min = 1
    g_max = 5
    grade_first_year = IntegerField(c.GRADE_FIRST_YEAR[c.LENGTH_OF_STUDY_DEFAULT], # noqa
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])
    grade_second_year = IntegerField(c.GRADE_SECOND_YEAR[c.LENGTH_OF_STUDY_DEFAULT],
                                     validators=[validators.Optional(),
                                                 validators.NumberRange(min=g_min,
                                                                        max=g_max,
                                                                        message=c.GRADE_ERR)])
    grade_third_year = IntegerField(c.GRADE_THIRD_YEAR[c.LENGTH_OF_STUDY_DEFAULT],
                                    validators=[validators.Optional(),
                                                validators.NumberRange(min=g_min,
                                                                       max=g_max,
                                                                       message=c.GRADE_ERR)])

class AdmissionWaiversForm(FlaskForm):
    further_study_info = FormField(FurtherStudyInfoForm,
                                   label=c.FURTHER_STUDY_INFO)

    grades_mat = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_MAT)
    grades_inf = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_INF)
    grades_fyz = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_FYZ)
    grades_bio = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_BIO)
    grades_che = FormField(FurtherGradesInfoForm,
                           label=c.GRADES_CHE)

    competition_1 = FormField(CompetitionSuccessFormItem,
                              label=c.COMPETITION_FIRST)
    competition_2 = FormField(CompetitionSuccessFormItem,
                              label=c.COMPETITION_SECOND)
    competition_3 = FormField(CompetitionSuccessFormItem,
                              label=c.COMPETITION_THIRD)
    admissions_waivers = HiddenField()
    submit = SubmitField(label=c.NEXT)


class FinalForm(FlaskForm):
    note = TextAreaField(label=c.FINAL_NOTE,
                         description=c.FINAL_NOTE_DESC)
    submit = SubmitField(label=c.SUBMIT_APPLICATION)


class ReceiptUploadForm(FlaskForm):
        receipt = FileField(label=c.PAYMENT_RECEIPT,
                            validators=[FileAllowed(c.receipts,
                                                    c.ERR_EXTENSION_NOT_ALLOWED), # noqa
                                        FileRequired(c.ERR_EMPTY_FILE)])
        submit = SubmitField(label=c.SUBMIT)


class LoginForm(FlaskForm):
    email = StringField(label=c.EMAIL,
                        validators=[validators.Email()])
    password = PasswordField(label=c.PASSWORD,
                             validators=[validators.Length(min=8, max=80)])
    submit = SubmitField(label=c.LOGIN)


class ForgottenPasswordForm(FlaskForm):
    email = StringField(label=c.EMAIL,
                        validators=[validators.Email()])
    submit = SubmitField(label=c.SUBMIT)


class NewPasswordForm(FlaskForm):
    password = PasswordField(label=c.PASSWORD,
                             validators=[validators.Length(min=8, max=80)])
    repeat_password = PasswordField(label=c.REPEAT_PASSWORD,
                                    validators=[validators.Length(min=8,
                                                                  max=80),
                                                validators.EqualTo('password',
                                                                   message=c.REPEAT_PASSWORD_ERR)])
    submit = SubmitField(label=c.SIGNUP)


class SignupForm(FlaskForm):
    email = StringField(label='',
                        validators=[validators.Email(),
                                    EmailDuplicateValidator()],
                        render_kw={"placeholder": c.EMAIL})
    submit = SubmitField(label=c.SIGNUP)


class AIS2CookieForm(FlaskForm):
    jsessionid = StringField(label='JSESSIONID',
                             validators=[validators.DataRequired()])
    submit = SubmitField(label=c.SUBMIT)


class AIS2SubmitForm(FlaskForm):
    submit = SubmitField(label=c.CONTINUE)
