import pickle
from urllib.parse import quote_plus
from flask import (render_template, flash, redirect, session, request, url_for,
                   make_response, send_from_directory)
import flask.json
from flask_mail import Message
from flask_uploads import UploadNotAllowed
from eprihlaska import app, db, mail, oauth
from eprihlaska.forms import (StudyProgrammeForm, PersonalDataForm,
                              AddressForm, PreviousStudiesForm,
                              AdmissionWaiversForm, FinalForm,
                              ReceiptUploadForm, LoginForm, SignupForm,
                              ForgottenPasswordForm, NewPasswordForm,
                              AIS2SubmitForm)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import datetime
import uuid
import sys
import traceback
import os

from munch import munchify
from functools import wraps

from .headless_pdfkit import generate_pdf
from .models import User, ApplicationForm, TokenModel, ForgottenPasswordToken
from .consts import (MENU, STUDY_PROGRAMME_CHOICES, FORGOTTEN_PASSWORD_MAIL,
                     NEW_USER_MAIL, SEX_CHOICES, COUNTRY_CHOICES, CITY_CHOICES,
                     CITY_CHOICES_PSC, MARITAL_STATUS_CHOICES,
                     HIGHSCHOOL_CHOICES, HS_STUDY_PROGRAMME_CHOICES,
                     HS_STUDY_PROGRAMME_MAP, EDUCATION_LEVEL_CHOICES,
                     COMPETITION_CHOICES, APPLICATION_STATES,
                     CURRENT_MATURA_YEAR, DEFAULT_MATURA_YEAR,
                     ApplicationStates)
from . import consts

STUDY_PROGRAMMES = list(map(lambda x: x[0], STUDY_PROGRAMME_CHOICES))
LISTS = {
    'sex': dict(SEX_CHOICES),
    'marital_status': dict(MARITAL_STATUS_CHOICES),
    'country': dict(COUNTRY_CHOICES),
    'city': dict(CITY_CHOICES),
    'city_psc': dict(CITY_CHOICES_PSC),
    'highschool': dict(HIGHSCHOOL_CHOICES),
    'hs_study_programme': dict(HS_STUDY_PROGRAMME_CHOICES),
    'education_level': dict(EDUCATION_LEVEL_CHOICES),
    'study_programme': dict(STUDY_PROGRAMME_CHOICES),
    'competition': dict(COMPETITION_CHOICES)
}


def require_filled_form(form_key):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rule = request.url_rule
            if 'application_submitted' in session:
                if 'final' not in rule.rule:
                    return redirect(final)

            # If submissions are not open, all of the other endpoints needs to
            # forward to homepage.
            if not app.config['SUBMISSIONS_OPEN'] and 'final' not in rule.rule:
                flash(consts.SUBMISSIONS_NOT_OPEN, 'error')
                return redirect(url_for('index'))

            if request.method == 'GET' and form_key not in session:
                flash(consts.FLASH_MSG_FILL_FORM)
                for _, endpoint in MENU:
                    if endpoint not in session:
                        return redirect(url_for(endpoint))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_remote_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not app.debug:
            if request.environ.get('REMOTE_USER') is None:
                flash(consts.NO_ACCESS_MSG, 'error')
                return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wrapper


def save_form(form):
    ignored_keys = ['csrf_token', 'submit']
    for k in form.data:
        if k not in ignored_keys:
            session[k] = form.data[k]
    if 'application_submit_refresh' in session:
        # FIXME: Get rid of this band-aid
        del session['application_submit_refresh']
        if 'application_submitted' in session:
            del session['application_submitted']

    save_current_session_to_DB()


def current_session_to_json():
    # Don't store internal keys used by flask (e.g. "_flashes"), flask-login
    # (e.g. "_user_id", "_fresh", "_id") and our admin ("_votr_context_*") in
    # the SQL database.
    filtered = { k: v for k, v in session.items() if not k.startswith('_') }
    return flask.json.dumps(filtered)


def save_current_session_to_DB():
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    app.application = current_session_to_json()
    db.session.commit()


@app.before_request
def load_session():
    global session
    # Only load the session form the DB if the current_user has an id (has been
    # logged in)
    if hasattr(current_user, 'id'):
        app = ApplicationForm.query.filter_by(user_id=current_user.id).first()

        # If the session in the DB is not set (is None), do not try  to load it
        if app.application is None:
            return

        d = flask.json.loads(app.application)
        for k in d:
            session[k] = d[k]

        if 'application_submit_refresh' in session:
            # FIXME: Get rid of this band-aid
            del session['application_submit_refresh']
            if 'application_submitted' in session:
                del session['application_submitted']

            app.application = current_session_to_json()
            db.session.commit()

        session.modified = True


@app.route('/')
def index():
    form = SignupForm()
    if hasattr(current_user, 'id') and app.config['SUBMISSIONS_OPEN']:
        return redirect(url_for('study_programme'))

    return render_template('intro.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES),
                           submissions_open=app.config['SUBMISSIONS_OPEN'])


@app.route('/study_programme', methods=('GET', 'POST'))
@login_required
def study_programme():
    # If the application has been submitted already, forward to the final
    # endpoint
    if 'application_submitted' in session:
        return redirect(url_for('final'))

    # If submissions are not open, forward to index
    if not app.config['SUBMISSIONS_OPEN']:
        return redirect(url_for('index'))

    form = StudyProgrammeForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            # Save study programmes into a list
            study_programme = []
            for sp in ['study_programme_1', 'study_programme_2',
                       'study_programme_3']:
                study_programme.append(session['study_programme_data'][sp])

            session['study_programme'] = study_programme

            set_ssp = set([x for x in study_programme if x != '_'])
            list_ssp = list([x for x in study_programme if x != '_'])

            # Ensure there are no duplicates within the study_programme list
            if len(set_ssp) != len(list_ssp):
                flash(consts.SELECT_STUDY_PROGRAMME_ONCE, 'error')
                return redirect(url_for('study_programme'))

            # Select at least one study programme
            if study_programme[0] == '_':
                flash(consts.SELECT_STUDY_PROGRAMME, 'error')
                return redirect(url_for('study_programme'))

            save_form(form)
            flash(consts.FLASH_MSG_DATA_SAVED)
        return redirect(url_for('personal_info'))
    else:
        if request.method == 'POST':
            flash(consts.FLASH_MSG_DATA_NOT_SAVED, 'error')

    return render_template('study_programme.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/personal_info', methods=('GET', 'POST'))
@login_required
@require_filled_form('index')
def personal_info():
    form = PersonalDataForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        save_form(form)

        flash(consts.FLASH_MSG_DATA_SAVED)
        return redirect(url_for('address'))
    else:
        if request.method == 'POST':
            flash(consts.FLASH_MSG_DATA_NOT_SAVED, 'error')

    return render_template('personal_info.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/address', methods=('GET', 'POST'))
@login_required
@require_filled_form('personal_info')
def address():
    form = AddressForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash(consts.FLASH_MSG_DATA_SAVED)
        return redirect(url_for('previous_studies'))
    else:
        if request.method == 'POST':
            flash(consts.FLASH_MSG_DATA_NOT_SAVED, 'error')

    return render_template('address.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/previous_studies', methods=('GET', 'POST'))
@login_required
@require_filled_form('address')
def previous_studies():
    form = PreviousStudiesForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash(consts.FLASH_MSG_DATA_SAVED)
        return redirect(url_for('admissions_waivers'))
    else:
        if request.method == 'POST':
            flash(consts.FLASH_MSG_DATA_NOT_SAVED, 'error')

    return render_template('previous_studies.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


def filter_competitions(competition_list, study_programme_list):
    result_list = []

    constraint_profiles = {
        'F': ['mBMF', 'FYZ', 'FYZ/k', 'OZE', 'OZE/k', 'TEF', 'TEF/k', 'upFYIN', 'upMAFY', 'upFYBI'],
        'I': ['INF', 'INF/k', 'AIN', 'BIN', 'BIN/k', 'DAV', 'DAV/k', 'upFYIN', 'upINBI', 'upMAIN', 'upINAN', 'upINGE', 'upINCH'],
        'B': ['BIN', 'BIN/k', 'mBMF'],
        'CH': ['mBMF','BIN', 'BIN/k']
    }

    constraints = {
        'FYZ': constraint_profiles['F'],
        'INF': constraint_profiles['I'],
        'BIO': constraint_profiles['B'],
        'CHM': constraint_profiles['CH'],
        'SOC_INF': constraint_profiles['I'],
        'SOC_BIO': constraint_profiles['B'],
        'SOC_CHM': constraint_profiles['CH'],
        'TMF': constraint_profiles['F'],
        'FVAT_FYZ': constraint_profiles['F'],
        'FVAT_INF': constraint_profiles['I'],
        'ROBOCUP': constraint_profiles['I'],
        'IBOBOR': constraint_profiles['I'],
        'ZENIT': constraint_profiles['I'],
        'TROJSTEN_KSP': constraint_profiles['I'],
        'TROJSTEN_FKS': constraint_profiles['F'],
        '_': STUDY_PROGRAMMES
    }

    for comp, desc in competition_list:
        if comp in ['MAT', 'SOC_MAT', 'FVAT_MAT', 'TROJSTEN_KMS']:
            result_list.append((comp, desc))

        for c, sp_list in constraints.items():
            if comp == c and set(sp_list) & set(study_programme_list):
                result_list.append((comp, desc))
    return result_list


@app.route('/admissions_waivers', methods=('GET', 'POST'))
@login_required
@require_filled_form('previous_studies')
def admissions_waivers():

    basic_data = session['basic_personal_data']
    if basic_data['dean_invitation_letter'] \
       and basic_data['dean_invitation_letter_no']:
        # Pretend the admission_waivers form has been filled in
        session['admissions_waivers'] = ''
        flash(consts.DEAN_LIST_MSG)
        return redirect(url_for('final'))

    form = AdmissionWaiversForm(obj=munchify(dict(session)))

    # Filter out competitions based on selected study programmes.
    for subform in form:
        if subform.id.startswith('competition_'):
            choices = subform.competition.choices
            new_choices = filter_competitions(choices,
                                              session['study_programme'])
            subform.competition.choices = new_choices

    grade_constraints = {
        'grades_mat': ['mBMF', 'FYZ', 'FYZ/k', 'OZE', 'OZE/k', 'TEF', 'TEF/k', 'BIN', 'BIN/k', 'DAV', 'DAV/k', 'AIN', 'INF', 'EFM', 'MMN', 'MAT', 'PMA'],
        'grades_inf': ['BIN', 'BIN/k', 'INF', 'INF/k', 'DAV', 'DAV/k', 'AIN'],
        'grades_fyz': ['mBMF', 'FYZ', 'FYZ/k', 'OZE', 'OZE/k', 'TEF', 'TEF/k'],
        'grades_bio': ['mBMF', 'BIN', 'BIN/k'],
        'grades_che': ['mBMF', 'BIN', 'BIN/k'],
    }

    # Set labels for grades of respective study years based on
    # `length_of_study`
    los = session['length_of_study']
    for grade_key in grade_constraints.keys():
        form[grade_key].grade_first_year.label.text = consts.GRADE_FIRST_YEAR[los] # noqa
        form[grade_key].grade_second_year.label.text = consts.GRADE_SECOND_YEAR[los] # noqa
        form[grade_key].grade_third_year.label.text = consts.GRADE_THIRD_YEAR[los] # noqa

    further_study_info_constraints = {
        'matura_mat_grade': ['AIN', 'upFYIN', 'upINAN', 'upINBI', 'upINGE',
                             'upINCH', 'upMADG', 'upMAFY', 'upMAIN', 'upMATV', 'upFYBI'],
        'matura_fyz_grade': ['upFYIN', 'upMAFY', 'upFYBI'],
        'matura_inf_grade': ['AIN', 'upFYIN', 'upINBI', 'upMAIN', 'upINAN',
                             'upINGE', 'upINCH'],
        'matura_bio_grade': [],
        'matura_che_grade': [],
    }

    further_study_info_constraints.update({
        'will_take_mat_matura': further_study_info_constraints['matura_mat_grade'], # noqa
        'will_take_fyz_matura': further_study_info_constraints['matura_fyz_grade'], # noqa
        'will_take_inf_matura': further_study_info_constraints['matura_inf_grade'], # noqa
        'will_take_bio_matura': further_study_info_constraints['matura_bio_grade'], # noqa
        'will_take_che_matura': further_study_info_constraints['matura_che_grade'], # noqa
    })

    relevant_years_last4 = [DEFAULT_MATURA_YEAR-3, DEFAULT_MATURA_YEAR-2,
                            DEFAULT_MATURA_YEAR-1, CURRENT_MATURA_YEAR-1]

    relevant_years = {
        'external_matura_percentile': relevant_years_last4,
        'matura_mat_grade': relevant_years_last4,
        'matura_fyz_grade': relevant_years_last4,
        'matura_inf_grade': relevant_years_last4,
        'matura_bio_grade': relevant_years_last4,
        'matura_che_grade': relevant_years_last4,
        'will_take_external_mat_matura': [CURRENT_MATURA_YEAR],
        'will_take_mat_matura': [CURRENT_MATURA_YEAR],
        'will_take_fyz_matura': [CURRENT_MATURA_YEAR],
        'will_take_inf_matura': [CURRENT_MATURA_YEAR],
        'will_take_bio_matura': [CURRENT_MATURA_YEAR],
        'will_take_che_matura': [CURRENT_MATURA_YEAR],
    }

    further_study_whitelist = [
        'scio_percentile',
        'scio_date',
        'will_take_scio'
    ]

    study_programme_set = set(session['study_programme'])
    matura_year = session['basic_personal_data']['matura_year']
    for k, v in grade_constraints.items():
        if not study_programme_set & set(v) or \
           matura_year not in relevant_years_last4 + [DEFAULT_MATURA_YEAR]:
            form.__delitem__(k)

    for k, v in further_study_info_constraints.items():
        if not study_programme_set & set(v):
            if k in form['further_study_info']._fields:
                form['further_study_info'].__delitem__(k)

    for k, v in relevant_years.items():
        if matura_year not in v:
            if k in form['further_study_info']._fields and \
                    k not in further_study_whitelist:
                form['further_study_info'].__delitem__(k)

    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash(consts.FLASH_MSG_DATA_SAVED)
        return redirect(url_for('final'))
    else:
        if request.method == 'POST':
            flash(consts.FLASH_MSG_DATA_NOT_SAVED, 'error')

    return render_template('admission_waivers.html', form=form,
                           session=session, sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/final', methods=['GET', 'POST'])
@login_required
@require_filled_form('admissions_waivers')
def final():
    app_form = ApplicationForm.query.filter_by(user_id=current_user.id).first()

    # If the application has not gone through the submission step (that is, it
    # is in in_progress state) and submissions are not open, we should redirect
    # to the front page with an error message saying 'submissions are not open'
    if not app.config['SUBMISSIONS_OPEN'] \
       and app_form.state == ApplicationStates.in_progress:
        flash(consts.SUBMISSIONS_NOT_OPEN, 'error')
        return redirect(url_for('index'))

    specific_symbol = 10000 + app_form.id

    hs_sp_check = True
    hs_education_level_check = True
    if session['finished_highschool_check'] == 'SK':
        # Check whether the highschool/study_programme_code pair
        # exists in the mapping list
        pair = (session['studies_in_sr']['highschool'],
                session['studies_in_sr']['study_programme_code'])
        study_programme_code_not_empty = (pair[1] != 'XXXXXX')
        filled_items = (pair[0] != 'XXXXXXX',
                        study_programme_code_not_empty)

        # Only check for the pair if both of the items (highschool and
        # study_programme_code) have been filled in.
        if all(filled_items) and pair not in HS_STUDY_PROGRAMME_MAP:
            hs_sp_check = False

        # Check whether the education_level code is actually present in
        # the study_programme_code
        el = session['studies_in_sr']['education_level']
        if study_programme_code_not_empty and \
           el not in session['studies_in_sr']['study_programme_code']:
            hs_education_level_check = False

    # Check whether any grades were actually filled in
    grades = []
    for x in session:
        if x.startswith('grades_'):
            for y in session[x]:
                if y.startswith('grade_'):
                    grades.append(session[x][y])
    grades_filled = any(map(lambda x: x is not None, grades))

    # Deal with receipt form
    receipt_form = None
    # If the application is no longer in progress (i.e. it has been either
    # submitted, printed or processed already), only then show the receipt_form
    if app_form.state != consts.ApplicationStates.in_progress:
        if 'receipt_filename' not in session:
            receipt_form = ReceiptUploadForm(obj=munchify(dict(session)))
            if receipt_form.validate_on_submit():
                filename = consts.receipts.save(receipt_form.receipt.data)
                session['receipt_filename'] = filename

                save_current_session_to_DB()

                flash(consts.FLASH_MSG_RECEIPT_SUBMITTED)

    form = FinalForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            session['application_submitted'] = True
            app_form.application = current_session_to_json()
            app_form.state = ApplicationStates.submitted
            app_form.submitted_at = datetime.datetime.now()
            db.session.commit()

            # The receipt_form should now be operational, as the application is
            # submitted
            receipt_form = ReceiptUploadForm(obj=munchify(dict(session)))

            flash(consts.FLASH_MSG_APP_SUBMITTED)

    app_state = APPLICATION_STATES[app_form.state.value]

    return render_template('final.html', session=session,
                           specific_symbol=specific_symbol,
                           sp=dict(STUDY_PROGRAMME_CHOICES),
                           hs_sp_check=hs_sp_check,
                           hs_ed_level_check=hs_education_level_check,
                           grades_filled=grades_filled,
                           app_state=app_state,
                           form=form, receipt_form=receipt_form,
                           consts=consts,uploads_enabled=app.config['UPLOADS_ENABLED'])


@app.route('/payment_receipt', methods=['GET'])
@login_required
def payment_receipt():
    if 'receipt_filename' not in session:
        flash(consts.ERR_RECEIPT_NOT_UPLOADED, 'error')
        return redirect(url_for('final'))

    root_dir = os.getcwd()
    receipt_dir = os.path.join(root_dir, app.config['UPLOADED_RECEIPTS_DEST'])
    return send_from_directory(receipt_dir, session['receipt_filename'],
                               as_attachment=True)


@app.route('/file/upload', methods=['POST'])
@login_required
def file_upload():
    if 'file' not in request.files:
        flash(consts.ERR_FILE_UPLOAD_ERROR, 'error')
        return redirect(url_for('final'))

    if 'uploaded_files' not in session:
        session['uploaded_files'] = []

    # Ensure that the uploaded file is saved to a subdir with the current
    # user's ID (i.e. a unique one).
    try:
        filename = consts.uploaded_files.save(request.files['file'],
                                              folder=str(current_user.id))
    except UploadNotAllowed:
        flash(consts.ERR_EXTENSION_NOT_ALLOWED, 'error')
        return redirect(url_for('final'))

    session['uploaded_files'].append({
        'uuid': str(uuid.uuid4()),
        'type': request.form.get('uploaded_document_type'),
        'file': filename
    })

    save_current_session_to_DB()

    flash(consts.FLASH_MSG_FILE_SUBMITTED)
    return redirect(url_for('final'))


@app.route('/file/download/<uuid>', methods=['GET'])
@login_required
def file_download(uuid):
    uploaded_files = session.get('uploaded_files', [])
    filtered = list(filter(lambda x: x['uuid'] == uuid, uploaded_files))

    if len(filtered) < 1:
        flash(consts.ERR_FILE_DOES_NOT_EXIST)
        return redirect(url_for('final'))

    file = filtered[0]['file']

    root_dir = os.getcwd()
    receipt_dir = os.path.join(root_dir, app.config['UPLOADED_UPFILES_DEST'])
    return send_from_directory(receipt_dir, file, as_attachment=True)


@app.route('/file/delete/<uuid>', methods=['GET'])
@login_required
def file_delete(uuid):
    uploaded_files = session.get('uploaded_files', [])
    filtered = list(filter(lambda x: x['uuid'] == uuid, uploaded_files))

    if len(filtered) < 1:
        flash(consts.ERR_FILE_DOES_NOT_EXIST)
        return redirect(url_for('final'))

    file = filtered[0]['file']

    root_dir = os.getcwd()
    file_path = os.path.join(root_dir, app.config['UPLOADED_UPFILES_DEST'],
                             file)
    os.unlink(file_path)

    new_uploaded_files = list(filter(lambda x: x['uuid'] != uuid,
                                     uploaded_files))
    session['uploaded_files'] = new_uploaded_files

    save_current_session_to_DB()

    flash(consts.FLASH_MSG_FILE_REMOVED)
    return redirect(url_for('final'))


@app.route('/grades_control', methods=['GET'])
@login_required
def grades_control():
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    rendered = render_template('grade_listing.html',
                               session=session,
                               id=app.id,
                               consts=consts)

    pdf = generate_pdf(rendered, options={'orientation': 'landscape',
                                          'quiet': ''})

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    disposition = 'inline; filename=grades_control.pdf'
    response.headers['Content-Disposition'] = disposition
    return response


def render_app(app, print=False, use_app_session=True):
    sess = session
    if use_app_session:
        sess = flask.json.loads(app.application)

    specific_symbol = 10000 + app.id
    rendered = render_template('application_form.html', session=sess,
                               lists=LISTS, id=app.id,
                               specific_symbol=specific_symbol,
                               submitted_at=app.submitted_at,
                               consts=consts, print=print)
    return rendered


@app.route('/application_form', methods=['GET'])
@login_required
def application_form():
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    rendered = render_app(app, use_app_session=False)

    pdf = generate_pdf(rendered, options={'quiet': ''})

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    disposition = 'inline; filename=application_form.pdf'
    response.headers['Content-Disposition'] = disposition
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password:
            if check_password_hash(user.password, form.password.data):
                logout_user()
                session.clear()
                login_user(user)

                # set the index endpoint as already visited (in order for the
                # menu generation to work correctly)
                session['index'] = ''

                flash(consts.LOGIN_CONGRATS_MSG)
                return redirect(url_for('study_programme'))
        flash(consts.FLASH_MSG_WRONG_LOGIN, 'error')

    return render_template('login.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


def send_password_email(user, title, body_template):
    hash = str(uuid.uuid4())
    valid_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    token = ForgottenPasswordToken(hash=hash,
                                   user_id=user.id,
                                   valid_until=valid_time)
    db.session.add(token)
    db.session.commit()

    link = url_for('forgotten_password_hash', hash=hash, _external=True)
    msg = Message(title)
    msg.body = body_template.format(link)
    msg.recipients = [user.email]

    # Only send the email in non-debug state
    if not app.debug:
        mail.send(msg)
    return link


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(email=form.email.data)
        db.session.add(new_user)
        db.session.commit()

        # pre-populate the email field in the form using the email provided at
        # signup time
        session['email'] = form.email.data

        session['basic_personal_data'] = {}
        session['address_form'] = {}
        session['correspondence_address'] = {}
        session['studies_in_sr'] = {}

        new_application_form = ApplicationForm(user_id=new_user.id)
        # FIXME: band-aid for last_updated_at
        new_application_form.last_updated_at = datetime.datetime.now()
        new_application_form.application = current_session_to_json()
        db.session.add(new_application_form)
        db.session.commit()

        link = send_password_email(new_user,
                                   'ePrihlaska - registrácia',
                                   NEW_USER_MAIL)

        msg = consts.NEW_USER_MSG
        if app.debug:
            msg += '\n{}'.format(link)
        flash(msg)

    return render_template('signup.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    session.clear()

    if request.environ.get('REMOTE_USER'):
        # Admin logout: clear our session, mod_shib session, and IdP session.
        # (return parameter doesn't matter, Shibboleth IdP ignores it.)
        return redirect('/Shibboleth.sso/Logout?return=/')

    return redirect(url_for('index'))


@app.route('/new_password/<hash>', methods=['GET', 'POST'])
def forgotten_password_hash(hash):
    token = ForgottenPasswordToken.query.filter_by(hash=hash).first()
    valid_time = (token.valid_until - datetime.datetime.now()).total_seconds()
    if token and token.valid and valid_time > 0:
        form = NewPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(id=token.user_id).first()
            user.password = generate_password_hash(form.password.data) 

            # Invalidate the token so that it cannot be used another time
            token.valid = False
            db.session.add(user)
            db.session.add(token)
            db.session.commit()
            flash(consts.PASSWD_CHANGED_MSG)
            return redirect(url_for('login'))
        return render_template('forgotten_password.html',
                               form=form, session=session,
                               sp=dict(STUDY_PROGRAMME_CHOICES))
    else:
        token.valid = False
        db.session.add(token)
        db.session.commit()
        flash(consts.INVALID_TOKEN_MSG, 'error')
        return redirect(url_for('forgotten_password'))

    return redirect(url_for('index'))


@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    form = ForgottenPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        link = None
        if user:
            link = send_password_email(user, 'ePrihlaska - nové heslo',
                                       FORGOTTEN_PASSWORD_MAIL)

        msg = consts.FORGOTTEN_PASSWORD_MSG
        if app.debug:
            msg += '\n{}'.format(link)
        flash(msg)

    return render_template('forgotten_password.html', form=form,
                           session=session, sp=dict(STUDY_PROGRAMME_CHOICES))


def create_or_get_user_and_login(site, token, name, surname, email):
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

        # pre-populate the email field in the form using the email obtained
        # from `site`
        session['email'] = email
        session['basic_personal_data'] = {}
        session['basic_personal_data']['name'] = name
        session['basic_personal_data']['surname'] = surname

        session['address_form'] = {}
        session['correspondence_address'] = {}
        session['studies_in_sr'] = {}

        new_application_form = ApplicationForm(user_id=user.id)
        # FIXME: band-aid for last_updated_at
        new_application_form.last_updated_at = datetime.datetime.now()
        new_application_form.application = current_session_to_json()
        db.session.add(new_application_form)
        db.session.commit()

    # set the index endpoint as already visited (in order for the menu
    # generation to work correctly)
    session['index'] = ''

    login_user(user)
    TokenModel.save(site, token, user)
    flash(consts.FLASH_MSG_AFTER_LOGIN)


@app.route('/google/login', methods=['GET'])
def google_login():
    callback_uri = url_for('google_authorize', _external=True)
    return oauth.google.authorize_redirect(callback_uri)


@app.route('/google/auth', methods=['GET'])
def google_authorize():
    token = oauth.google.authorize_access_token()
    profile = oauth.google.userinfo(token=token)

    create_or_get_user_and_login('google', token,
                                 profile.get('given_name', ''),
                                 profile.get('family_name', ''),
                                 profile.email)

    return redirect(url_for('study_programme'))


def process_apps(apps):
    for application in apps:
        out_app = {}
        app_object = flask.json.loads(application.application)
        for key in app_object.keys():
            out_app[key] = app_object[key]

        # TODO: this is band-aid and should be removed
        if 'basic_personal_data' not in out_app:
            out_app['basic_personal_data'] = {}
        application.app = out_app
    return apps


def get_apps(s):
    apps = ApplicationForm.query \
            .filter_by(state=s) \
            .order_by(ApplicationForm.submitted_at.desc()).all()
    return process_apps(apps)


@app.route('/admin/list')
@require_remote_user
def admin_list():
    in_progress = get_apps(ApplicationStates.in_progress)
    submitted = get_apps(ApplicationStates.submitted)
    printed = get_apps(ApplicationStates.printed)
    processed = get_apps(ApplicationStates.processed)
    return render_template('admin_list.html', in_progress=in_progress,
                           submitted=submitted, printed=printed,
                           processed=processed, states=APPLICATION_STATES,
                           consts=consts)


@app.route('/admin/view/<id>')
@require_remote_user
def admin_view(id):
    app = ApplicationForm.query.get(id)
    rendered = render_app(app)
    return rendered


@app.route('/admin/print/<id>')
@require_remote_user
def admin_print(id):
    import pypdftk # noqa
    import tempfile

    app = ApplicationForm.query.get(id)

    rendered = render_app(app, print=True)
    pdf = generate_pdf(rendered, options={'quiet': ''})

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.write(pdf)

    n_pages = pypdftk.get_num_pages(fp.name)
    n_blank_pages = 3 - n_pages
    blank_path = consts.DIR + '/data/blank_A4.pdf'

    paths_to_concat = [fp.name]
    paths_to_concat += [blank_path] * n_blank_pages
    paths_to_concat += [consts.DIR + '/data/protokol.pdf']

    concated_file = pypdftk.concat(paths_to_concat)
    with open(concated_file, 'rb') as out_f:
        output = out_f.read()

    # remove the temp file
    os.unlink(fp.name)

    # mark the application as 'printed' in the DB
    app.state = ApplicationStates.printed
    app.printed_at = datetime.datetime.now()
    db.session.commit()

    response = make_response(output)
    response.headers['Content-Type'] = 'application/pdf'
    disposition = 'inline; filename=application_form_{}.pdf'.format(id)
    response.headers['Content-Disposition'] = disposition
    return response


@app.route('/admin/reset/<id>')
@require_remote_user
def admin_reset(id):
    app = ApplicationForm.query.get(id)
    app.state = ApplicationStates.in_progress
    sess = flask.json.loads(app.application)
    if 'application_submitted' in sess:
        del sess['application_submitted']
        sess['application_submit_refresh'] = True

    app.application = flask.json.dumps(dict(sess))
    db.session.commit()

    return redirect(url_for('admin_list'))


@app.route('/admin/set_state/<id>/<int:state>')
@require_remote_user
def admin_set_state(id, state):
    app = ApplicationForm.query.get(id)
    app.state = ApplicationStates(state)
    sess = flask.json.loads(app.application)

    # If application is set to submitted, set its session appropriately.
    if app.state == ApplicationStates.submitted:
        sess['application_submitted'] = True
        app.application = flask.json.dumps(dict(sess))
        app.submitted_at = datetime.datetime.now()

    db.session.commit()
    return redirect(url_for('admin_list'))


@app.route('/admin/payment_receipt/<id>')
@require_remote_user
def admin_payment_receipt(id):
    application = ApplicationForm.query.get(id)
    sess = flask.json.loads(application.application)

    root_dir = os.getcwd()
    receipt_dir = os.path.join(root_dir, app.config['UPLOADED_RECEIPTS_DEST'])
    return send_from_directory(receipt_dir, sess['receipt_filename'],
                               as_attachment=True)


@app.route('/admin/file/download/<id>/<uuid>', methods=['GET'])
@require_remote_user
def admin_file_download(id, uuid):
    application = ApplicationForm.query.get(id)
    sess = flask.json.loads(application.application)

    uploaded_files = sess.get('uploaded_files', [])
    filtered = list(filter(lambda x: x['uuid'] == uuid, uploaded_files))

    file = filtered[0]['file']

    root_dir = os.getcwd()
    receipt_dir = os.path.join(root_dir, app.config['UPLOADED_UPFILES_DEST'])
    return send_from_directory(receipt_dir, file, as_attachment=True)


@app.route('/admin/init_votr/<any(prod,beta):ais_instance>')
@require_remote_user
def admin_init_votr(ais_instance):
    next = request.args['next']
    if not next.startswith('/admin/'):
        return 'Bad next', 400

    from .ais_utils import create_context
    votr_context = create_context(
        my_entity_id=app.config['MY_ENTITY_ID'],
        andrvotr_api_key=app.config['ANDRVOTR_API_KEY'],
        andrvotr_authority_token=request.environ['ANDRVOTR_AUTHORITY_TOKEN'],
        beta=(ais_instance == 'beta'),
    )
    # flask-session docs say it'll stop using pickle in the future.
    # Wrap the votr_context in our own pickle.
    session[f'_votr_context_{ais_instance}'] = pickle.dumps(votr_context, pickle.HIGHEST_PROTOCOL)

    return redirect(next)


def require_votr_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ais_instance = kwargs['ais_instance']
        session_key = f'_votr_context_{ais_instance}'
        if not session.get(session_key):
            # First time we visited an admin page that requires votr_context?
            # 1. Re-login with mod_shib to get a fresh andrvotr authority token.
            # 2. Create a votr_context and store it in the flask session.
            # 3. Redirect back here.
            target = url_for('admin_init_votr', ais_instance=ais_instance, next=request.full_path)
            return redirect(f'/Shibboleth.sso/Login?target={quote_plus(target)}')

        votr_context = pickle.loads(session[session_key])
        result = func(*args, **kwargs, votr_context=votr_context)
        session[session_key] = pickle.dumps(votr_context, pickle.HIGHEST_PROTOCOL)
        return result
    return wrapper


@app.route('/admin/ais_test/<any(prod,beta):ais_instance>')
@require_remote_user
@require_votr_context
def admin_ais_test(ais_instance, votr_context):
    from .ais_utils import test_ais
    test_ais(votr_context)
    return redirect(url_for('admin_list'))


@app.route('/admin/submitted_stats')
@require_remote_user
def admin_submitted_stats():
    from werkzeug.datastructures import Headers
    from werkzeug.wrappers import Response
    from flask import stream_with_context

    def generate():
        import io
        import csv
        A = ApplicationForm \
            .query \
            .filter(ApplicationForm.submitted_at.isnot(None)) \
            .all()

        data = io.StringIO()

        w = csv.writer(data, delimiter='\t')
        w.writerow(('school', 'started_at', 'submitted_at'))

        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for application in A:
            sess = flask.json.loads(application.application)
            if not sess['finished_highschool_check'] == 'SK':
                continue

            user = User.query.filter_by(id=application.user_id).first()
            hs_code = sess['studies_in_sr']['highschool']
            highschool = LISTS['highschool'][hs_code]

            w.writerow((highschool,
                        user.registered_at,
                        application.submitted_at))

            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    headers = Headers()
    headers.set('Content-Disposition', 'attachment',
                filename='submitted_applications_stats.tsv')

    return Response(stream_with_context(generate()),
                    mimetype='text/tsv', headers=headers)


@app.route('/admin/scio_stats')
@require_remote_user
def admin_scio_stats():
    from werkzeug.datastructures import Headers
    from werkzeug.wrappers import Response
    from flask import stream_with_context

    def generate():
        import io
        import csv
        A = ApplicationForm \
            .query \
            .filter(ApplicationForm.submitted_at.isnot(None)) \
            .all()

        data = io.StringIO()

        w = csv.writer(data, delimiter='\t')
        w.writerow(('name', 'surname', 'birth_no', 'scio_percentile',
                    'scio_date'))

        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for application in A:
            sess = flask.json.loads(application.application)
            if 'further_study_info' not in sess:
                continue

            if 'scio_date' not in sess['further_study_info'] and \
               'scio_percentile' not in sess['further_study_info']:
                continue

            name = sess['basic_personal_data']['name']
            surname = sess['basic_personal_data']['surname']
            birth_no = sess['birth_no']
            scio_percentile = sess['further_study_info']['scio_percentile']
            scio_date = sess['further_study_info']['scio_date']

            if scio_date.strip() == scio_percentile.strip() == '':
                continue

            w.writerow((name, surname, birth_no,
                        scio_percentile, scio_date))

            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    headers = Headers()
    headers.set('Content-Disposition', 'attachment',
                filename='scio_stats.tsv')

    return Response(stream_with_context(generate()),
                    mimetype='text/tsv', headers=headers)


@app.route('/admin/ais2_process/<any(prod,beta):ais_instance>/<any(none,fill,no_fill):process_type>/<id>', methods=['GET', 'POST'])
@require_remote_user
@require_votr_context
def admin_ais2_process(ais_instance, process_type, id, votr_context):
    application = ApplicationForm.query.get(id)

    form = AIS2SubmitForm()

    from .ais_utils import save_application_form
    if form.validate_on_submit():
        ais2_output = None
        error_output = None
        notes = {}

        logfile = None
        try:
            if ais_instance == 'beta':
                import gzip
                import random
                logfile = gzip.open('/tmp/log_%s_%s' % (id, random.randrange(10000)), 'wt', encoding='utf8')
                votr_context.logger.log_file = logfile

            ais2_output, notes = save_application_form(votr_context,
                                                       application,
                                                       LISTS,
                                                       id,
                                                       process_type)
        except Exception:
            error_output = traceback.format_exception(*sys.exc_info())
            error_output = '\n'.join(error_output)
            title = '{} AIS2 (#{})'.format(app.config['ERROR_EMAIL_HEADER'],
                                           id)

            # Send email on AIS2 error
            msg = Message(title)
            msg.body = error_output
            msg.recipients = app.config['ADMINS']

            # Only send the email if we are not in the debug mode
            if not app.debug:
                mail.send(msg)
            else:
                print(error_output)

        if logfile: logfile.close()

        # Only update the application state of it is not sent to beta and the
        # 'person_exists' note is not added
        if ais_instance != 'beta' and error_output is None and 'person_exists' not in notes:
            application.state = ApplicationStates.processed
            db.session.commit()

        sess = flask.json.loads(application.application)
        return render_template('admin_process.html',
                               ais2_output=ais2_output,
                               notes=notes, id=id,
                               error_output=error_output,
                               ais_instance=ais_instance,
                               process_type=process_type,
                               session=sess,
                               lists=LISTS)

    return render_template('admin_process.html',
                           form=form, id=id,
                           ais_instance=ais_instance)


@app.route('/admin/impersonate/list')
@require_remote_user
def admin_impersonate_list():
    users = User.query.all()
    return render_template('admin_impersonate_list.html', users=users)


@app.route('/admin/impersonate/<id>')
@require_remote_user
def admin_impersonate_user(id):
    user = User.query.get(id)
    logout_user()
    session.clear()
    login_user(user)
    return redirect(url_for('index'))


@app.template_filter('get_user')
def get_user_filter(user_id):
    return User.query.get(user_id)


@app.route('/admin/tokens/list')
@require_remote_user
def admin_tokens_list():
    tokens = ForgottenPasswordToken.query.all()
    return render_template('admin_tokens_list.html', tokens=tokens)
