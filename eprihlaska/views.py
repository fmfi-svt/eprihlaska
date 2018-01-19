from flask import (render_template, flash, redirect, session, request, url_for,
                   make_response)
import flask.json
from flask_mail import Message
from eprihlaska import app, db, mail
from eprihlaska.forms import (StudyProgrammeForm, PersonalDataForm,
                              FurtherPersonalDataForm, AddressForm,
                              PreviousStudiesForm, AdmissionWaversForm,
                              LoginForm, SignupForm, ForgottenPasswordForm,
                              NewPasswordForm, AIS2CookieForm)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from authlib.client.apps import google, facebook
import datetime
import string
import uuid
import sys
import traceback

from munch import munchify
from functools import wraps

from .headless_pdfkit import generate_pdf
from .models import User, ApplicationForm, TokenModel, ForgottenPasswordToken
from .consts import (MENU, STUDY_PROGRAMME_CHOICES, FORGOTTEN_PASSWORD_MAIL,
                     NEW_USER_MAIL, SEX_CHOICES, COUNTRY_CHOICES, CITY_CHOICES,
                     CITY_CHOICES_PSC, MARITAL_STATUS_CHOICES,
                     HIGHSCHOOL_CHOICES, HS_STUDY_PROGRAMME_CHOICES,
                     HS_STUDY_PROGRAMME_MAP, EDUCATION_LEVEL_CHOICES,
                     COMPETITION_CHOICES, APPLICATION_STATES, ApplicationStates)
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
            if 'application_submitted' in session:
                rule = request.url_rule
                if 'final' not in rule.rule:
                    return redirect(final)

            if request.method == 'GET' and form_key not in session:
                flash('Najprv, prosím, vyplňte formulár uvedený nižšie')
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
                flash('Nemáte oprávnenie pre prístup k danému prístupovému bodu', 'error')
                return redirect(url_for('index'))
        return func(*args, **kwargs)
    return wrapper


def save_form(form):
    ignored_keys = ['csrf_token', 'submit']
    for k in form.data:
        if k not in ignored_keys:
            session[k] = form.data[k]
    if 'application_submit_refresh' in session:
        del session['application_submitted']
        del session['application_submit_refresh']

    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    app.application = flask.json.dumps(dict(session))
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
            del session['application_submitted']
            del session['application_submit_refresh']

            app.application = flask.json.dumps(dict(session))
            db.session.commit()

        session.modified = True

@app.route('/')
def index():
    form = SignupForm()
    if hasattr(current_user, 'id'):
        return redirect(url_for('study_programme'))

    return render_template('intro.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))

@app.route('/study_programme', methods=('GET', 'POST'))
@login_required
def study_programme():
    if 'application_submitted' in session:
        return redirect(url_for('final'))

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

            # Select at least one study programme
            if study_programme[0] == '_':
                flash('Vyberte si, prosím, aspoň prvý študijný program', 'error')
                return redirect(url_for('study_programme'))

            save_form(form)
            flash('Vaše dáta boli uložené!')
        return redirect(url_for('personal_info'))
    return render_template('study_programme.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/personal_info', methods=('GET', 'POST'))
@login_required
@require_filled_form('index')
def personal_info():
    form = PersonalDataForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        save_form(form)

        flash('Vaše dáta boli uložené!')
        return redirect(url_for('further_personal_info'))
    return render_template('personal_info.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))

@app.route('/further_personal_info', methods=('GET', 'POST'))
@login_required
@require_filled_form('personal_info')
def further_personal_info():
    form = FurtherPersonalDataForm(obj=munchify(dict(session)))

    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash('Vaše dáta boli uložené!')
        return redirect(url_for('address'))
    return render_template('further_personal_info.html', form=form,
                           session=session, sp=dict(STUDY_PROGRAMME_CHOICES))

@app.route('/address', methods=('GET', 'POST'))
@login_required
@require_filled_form('further_personal_info')
def address():
    form = AddressForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash('Vaše dáta boli uložené!')
        return redirect(url_for('previous_studies'))
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

            flash('Vaše dáta boli uložené!')
        return redirect(url_for('admissions_waivers'))
    return render_template('previous_studies.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))

def filter_competitions(competition_list, study_programme_list):
    result_list = []

    constraints = {
        'FYZ': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY'],
        'INF': ['INF', 'AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'BIO': ['BIN', 'BMF'],
        'CHE': ['BIN', 'BMF'],
        'SVOC_INF': ['INF', 'AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'SVOC_BIO': ['BIN', 'BMF'],
        'SVOC_CHM': ['BIN', 'BMF'],
        'TMF': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY'],
        '_': STUDY_PROGRAMMES
    }

    for comp, desc in competition_list:
        if comp in ['MAT', 'SVOC_MAT'] and 'upINAN' not in study_programme_list:
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
    if basic_data['dean_invitation_letter'] and basic_data['dean_invitation_letter_no']:
        # Pretend the admission_waivers form has been filled in
        session['admissions_waivers'] = ''
        flash('Na základe listu dekana nie je potrebné zadávať údaje o prospechu na strednej škole.')
        return redirect(url_for('final'))

    form = AdmissionWaversForm(obj=munchify(dict(session)))

    # Filter out competitions based on selected study programmes.
    for subform in form:
        if subform.id.startswith('competition_'):
            choices = subform.competition.choices
            new_choices = filter_competitions(choices, session['study_programme'])
            subform.competition.choices = new_choices

    grade_constraints = {
        'grades_mat': ['BMF', 'FYZ', 'OZE'],
        'grades_fyz': ['BMF', 'FYZ', 'OZE'],
        'grades_bio': ['BMF'],
    }

    further_study_info_constraints = {
        'matura_fyz_grade': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY'],
        'matura_inf_grade': ['INF', 'AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'matura_bio_grade': ['BIN', 'BMF'],
        'matura_che_grade': ['BIN', 'BMF'],
        'will_take_fyz_matura': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY'],
        'will_take_inf_matura': ['INF', 'AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'will_take_bio_matura': ['BIN', 'BMF'],
        'will_take_che_matura': ['BIN', 'BMF']

    }

    relevant_years = {
        'external_matura_percentile': [2014, 2015, 2016, 2017],
        'scio_percentile': [2014, 2015, 2016, 2017],
        'scio_date': [2014, 2015, 2016, 2017],
        'matura_mat_grade': [2015, 2016, 2017],
        'matura_fyz_grade': [2015, 2016, 2017],
        'matura_inf_grade': [2015, 2016, 2017],
        'matura_bio_grade': [2015, 2016, 2017],
        'matura_che_grade': [2015, 2016, 2017],
        'will_take_external_mat_matura': [2018],
        'will_take_scio': [2018],
        'will_take_mat_matura': [2018],
        'will_take_fyz_matura': [2018],
        'will_take_inf_matura': [2018],
        'will_take_bio_matura': [2018],
        'will_take_che_matura': [2018],
    }

    study_programme_set = set(session['study_programme'])
    matura_year = session['basic_personal_data']['matura_year']
    for k, v in grade_constraints.items():
        if not study_programme_set & set(v) or \
            matura_year not in [2015, 2016, 2017, 2018]:
            form.__delitem__(k)

    for k, v in further_study_info_constraints.items():
        if not study_programme_set & set(v):
            if k in form['further_study_info']._fields:
                form['further_study_info'].__delitem__(k)

    for k, v in relevant_years.items():
        if not matura_year in v:
            if k in form['further_study_info']._fields:
                form['further_study_info'].__delitem__(k)

    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash('Vaše dáta boli uložené!')
        return redirect(url_for('final'))

    return render_template('admission_waivers.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))

@app.route('/final', methods=['GET'])
@login_required
@require_filled_form('admissions_waivers')
def final():
    specific_symbol = 9999 + current_user.id

    hs_sp_check = True
    hs_education_level_check = True
    if session['finished_highschool_check'] == 'SK':
        # Check whether the highschool/study_programme_code pair
        # exists in the mapping list
        pair = (session['studies_in_sr']['highschool'],
                session['studies_in_sr']['study_programme_code'])
        if pair not in HS_STUDY_PROGRAMME_MAP:
            hs_sp_check = False

        # Check whether the education_level code is actually present in
        # the study_programme_code
        el = session['studies_in_sr']['education_level']
        if el not in session['studies_in_sr']['study_programme_code']:
            hs_education_level_check = False


    return render_template('final.html', session=session,
                           specific_symbol=specific_symbol,
                           sp=dict(STUDY_PROGRAMME_CHOICES),
                           hs_sp_check=hs_sp_check,
                           hs_ed_level_check=hs_education_level_check)


@app.route('/submit_app')
@login_required
def submit_app():
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    session['application_submitted'] = True
    app.application = flask.json.dumps(dict(session))
    app.state = ApplicationStates.submitted
    app.submitted_at = datetime.datetime.now()
    db.session.commit()

    flash('Gratulujeme, Vaša prihláška bola podaná!')
    return redirect(url_for('final'))

@app.route('/grades_control', methods=['GET'])
@login_required
def grades_control():
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    rendered = render_template('grade_listing.html', session=session,
                               id=app.id)
    pdf = generate_pdf(rendered, options={'orientation': 'landscape'})

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=grades_control.pdf'
    return response

def render_app(app, print=False, use_app_session=True):
    sess = session
    if use_app_session:
        sess = flask.json.loads(app.application)

    rendered = render_template('application_form.html', session=sess,
                               lists=LISTS, id=app.id,
                               submitted_at=app.submitted_at,
                               consts=consts, print=print)
    return rendered


@app.route('/application_form', methods=['GET'])
@login_required
def application_form():
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    rendered = render_app(app, use_app_session=False)

    pdf = generate_pdf(rendered)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=application_form.pdf'
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

                flash('Gratulujeme, boli ste prihlásení do prostredia ePrihlaska!')
                return redirect(url_for('study_programme'))
        flash('Nesprávne prihlasovacie údaje', 'error')

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
        session['mother_name'] = {}
        session['father_name'] = {}
        session['address_form'] = {}
        session['correspondence_address'] = {}
        session['studies_in_sr'] = {}

        new_application_form = ApplicationForm(user_id=new_user.id)
        # FIXME: band-aid for last_updated_at
        new_application_form.last_updated_at = datetime.datetime.now()
        new_application_form.application = flask.json.dumps(dict(session))
        db.session.add(new_application_form)
        db.session.commit()

        link = send_password_email(new_user, 'ePrihlaska - registrácia', NEW_USER_MAIL)
        msg = consts.NEW_USER_MSG
        if app.debug:
            msg += '\n{}'.format(link)
        flash(msg)

    return render_template('signup.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    # Clear out the session
    keys = list(session.keys()).copy()
    for k in keys:
        session.pop(k)

    logout_user()
    return redirect(url_for('index'))

@app.route('/new_password/<hash>', methods=['GET', 'POST'])
def forgotten_password_hash(hash):
    token = ForgottenPasswordToken.query.filter_by(hash=hash).first()
    valid_time = (token.valid_until - datetime.datetime.now()).total_seconds()
    if token and token.valid and valid_time > 0:
        form = NewPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(id=token.user_id).first()
            user.password = generate_password_hash(form.password.data,
                                                   method='sha256')

            # Invalidate the token so that it cannot be used another time
            token.valid = False
            db.session.add(user)
            db.session.add(token)
            db.session.commit()
            flash('Gratulujeme, Vaše heslo bolo nastavené! Prihláste sa ním, prosím, nižšie.')
            return redirect(url_for('login'))
        return render_template('forgotten_password.html', form=form, session=session,
                               sp=dict(STUDY_PROGRAMME_CHOICES))
    else:
        token.valid = False
        db.session.add(token)
        db.session.commit()
        flash('Váš token na zmenu hesla je neplatný. Vyplnte prosím Váš email znovu.', 'error')
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

    return render_template('forgotten_password.html', form=form, session=session,
                           sp=dict(STUDY_PROGRAMME_CHOICES))


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

        session['mother_name'] = {}
        session['father_name'] = {}
        session['address_form'] = {}
        session['correspondence_address'] = {}
        session['studies_in_sr'] = {}

        new_application_form = ApplicationForm(user_id=user.id)
        # FIXME: band-aid for last_updated_at
        new_application_form.last_updated_at = datetime.datetime.now()
        new_application_form.application = flask.json.dumps(dict(session))
        db.session.add(new_application_form)
        db.session.commit()

    # set the index endpoint as already visited (in order for the menu
    # generation to work correctly)
    session['index'] = ''

    login_user(user)
    TokenModel.save(site, token, user)
    flash('Gratulujeme, boli ste prihlásení do prostredia ePrihlaska!')

@app.route('/google/login', methods=['GET'])
def google_login():
    callback_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(callback_uri)

@app.route('/google/auth', methods=['GET'])
def google_authorize():
    token = google.authorize_access_token()
    profile = google.parse_openid(token)

    create_or_get_user_and_login('google', token, profile.data['given_name'],
                                 profile.data['family_name'], profile.email)

    return redirect(url_for('study_programme'))

@app.route('/facebook/login', methods=['GET'])
def facebook_login():
    callback_uri = url_for('facebook_authorize', _external=True)
    return facebook.authorize_redirect(callback_uri)

@app.route('/facebook/auth', methods=['GET'])
def facebook_authorize():
    token = facebook.authorize_access_token()
    profile = facebook.fetch_user()

    data = profile.data['name'].split(' ')
    name = '' if not len(data) else data[0]
    surname = '' if len(data) <= 1 else data[-1]

    create_or_get_user_and_login('facebook', token, name, surname, profile.email)

    return redirect(url_for('study_programme'))

def process_apps(apps):
    for app in apps:
        out_app = {}
        a = flask.json.loads(app.application)
        for key in a.keys():
            out_app[key] = a[key]

        # TODO: this is band-aid and should be removed
        if 'basic_personal_data' not in out_app:
            out_app['basic_personal_data'] = {}
        app.app = out_app
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
                           processed=processed, states=APPLICATION_STATES)


@app.route('/admin/view/<id>')
@require_remote_user
def admin_view(id):
    app = ApplicationForm.query.filter_by(id=id).first()
    rendered = render_app(app)
    return rendered

@app.route('/admin/print/<id>')
@require_remote_user
def admin_print(id):
    app = ApplicationForm.query.filter_by(id=id).first()
    app.state = ApplicationStates.printed
    app.printed_at = datetime.datetime.now()
    app.last_updated_by = request.environ.get('REMOTE_USER')
    db.session.commit()

    rendered = render_app(app, print=True)
    return rendered

@app.route('/admin/reset/<id>')
@require_remote_user
def admin_reset(id):
    app = ApplicationForm.query.filter_by(id=id).first()
    app.state = ApplicationStates.in_progress
    sess = flask.json.loads(app.application)
    if 'application_submitted' in sess:
        del sess['application_submitted']
        sess['application_submit_refresh'] = True

    app.last_updated_by = request.environ.get('REMOTE_USER')
    app.application = flask.json.dumps(dict(sess))
    db.session.commit()

    return redirect(url_for('admin_list'))

@app.route('/admin/process/<id>', methods=['GET', 'POST'])
@require_remote_user
def admin_process(id):
    application = ApplicationForm.query.filter_by(id=id).first()
    from .ais_utils import (create_context, save_application_form)

    form = AIS2CookieForm()
    if form.validate_on_submit():
        ctx = create_context({'JSESSIONID': form.data['jsessionid']})
        ais2_output = None
        error_output = None
        notes = {}

        try:
            ais2_output, notes = save_application_form(ctx,
                                                       application,
                                                       LISTS,
                                                       id)
        except Exception as e:
            error_output = traceback.format_exception(*sys.exc_info())
            error_output = '\n'.join(error_output)
            title = '{} AIS2'.format(app.config['ERROR_EMAIL_HEADER'])

            # Send email on AIS2 error
            msg = Message(title)
            msg.body = body_template.format(error_output)
            msg.recipients = app.config['ADMINS']

            # Only send the email if we are not in the debug mode
            if not app.debug:
                mail.send(msg)
            else:
                print(error_output)

        if error_output is None:
            application.state = ApplicationStates.processed
            db.session.commit()

        return render_template('admin_process.html',
                               ais2_output=ais2_output,
                               notes=notes, id=id,
                               error_output=error_output)

    return render_template('admin_process.html',
                           form=form, id=id)
