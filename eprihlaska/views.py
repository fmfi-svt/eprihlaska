from flask import (render_template, flash, redirect, session, request, url_for,
                   make_response)
import flask.json
from flask_mail import Message
from eprihlaska import app, db, mail
from eprihlaska.forms import (StudyProgrammeForm, PersonalDataForm,
                              FurtherPersonalDataForm, AddressForm,
                              PreviousStudiesForm, AdmissionWaversForm,
                              LoginForm, SignupForm, ForgottenPasswordForm,
                              NewPasswordForm)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from authlib.client.apps import google, facebook
import datetime
import string
import uuid

from munch import munchify
from functools import wraps

from .models import User, ApplicationForm, TokenModel, ForgottenPassworToken
from .consts import (MENU, STUDY_PROGRAMME_CHOICES, FORGOTTEN_PASSWORD_MAIL,
                     SEX_CHOICES, COUNTRY_CHOICES, CITY_CHOICES,
                     MARITAL_STATUS_CHOICES, HIGHSCHOOL_CHOICES,
                     HS_STUDY_PROGRAMME_CHOICES, EDUCATION_LEVEL_CHOICES)

STUDY_PROGRAMMES = list(map(lambda x: x[0], STUDY_PROGRAMME_CHOICES))


def require_filled_form(form_key):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'application_submitted' in session:
                final = url_for('final')
                if str(request.url_rule) != final:
                    return redirect(final)

            if request.method == 'GET' and form_key not in session:
                flash('Najprv, prosím, vyplňte formulár uvedený nižšie')
                for _, endpoint in MENU:
                    if endpoint not in session:
                        return redirect(url_for(endpoint))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def save_form(form):
    ignored_keys = ['csrf_token', 'submit']
    for k in form.data:
        if k not in ignored_keys:
            session[k] = form.data[k]
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
        session.modified = True

@app.route('/')
def index():
    return render_template('intro.html', session=session)

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

            save_form(form)
            flash('Vaše dáta boli uložené!')
        return redirect('/personal_info')
    return render_template('study_programme.html', form=form, session=session)


@app.route('/personal_info', methods=('GET', 'POST'))
@login_required
@require_filled_form('index')
def personal_info():
    form = PersonalDataForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        save_form(form)

        flash('Vaše dáta boli uložené!')
        return redirect('/further_personal_info')
    return render_template('personal_info.html', form=form, session=session)

@app.route('/further_personal_info', methods=('GET', 'POST'))
@login_required
@require_filled_form('personal_info')
def further_personal_info():
    form = FurtherPersonalDataForm(obj=munchify(dict(session)))

    # Do not show `birth_no` field if the user does not come from SK/CZ.
    # Do show it, however, if the user did not fill in their nationality yet.
    if session.get('nationality') not in ['703', '203', None]:
        form['basic_personal_data'].__delitem__('birth_no')

    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash('Vaše dáta boli uložené!')
        return redirect('/address')
    return render_template('further_personal_info.html', form=form,
                           session=session)

@app.route('/address', methods=('GET', 'POST'))
@login_required
@require_filled_form('further_personal_info')
def address():
    form = AddressForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash('Vaše dáta boli uložené!')
        return redirect('/previous_studies')
    return render_template('address.html', form=form, session=session)

@app.route('/previous_studies', methods=('GET', 'POST'))
@login_required
@require_filled_form('address')
def previous_studies():
    form = PreviousStudiesForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        if 'application_submitted' not in session:
            save_form(form)

            flash('Vaše dáta boli uložené!')
        return redirect('/admissions_wavers')
    return render_template('previous_studies.html', form=form, session=session)

def filter_competitions(competition_list, study_programme_list):
    result_list = []

    constraints = {
        'FYZ': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY'],
        'INF': ['AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'BIO': ['BIN', 'BMF'],
        'CHE': ['BIN', 'BMF'],
        'SVOC_INF': ['AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
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

@app.route('/admissions_wavers', methods=('GET', 'POST'))
@login_required
@require_filled_form('previous_studies')
def admissions_wavers():

    basic_data = session['basic_personal_data']
    if basic_data['dean_invitation_letter'] and basic_data['dean_invitation_letter_no']:
        # Pretend the admission_wavers form has been filled in
        session['admissions_wavers'] = ''
        flash('Na základe listu od dekana Vám bolo prijímacie konanie ' +
              'odpustené.')
        return redirect('/final')

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
        'matura_inf_grade': ['AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'matura_bio_grade': ['BIN', 'BMF'],
        'matura_che_grade': ['BIN', 'BMF'],
        'will_take_fyz_matura': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY'],
        'will_take_inf_matura': ['AIN', 'BIN', 'upINBI', 'upMAIN', 'upINAN'],
        'will_take_bio_matura': ['BIN', 'BMF'],
        'will_take_che_matura': ['BIN', 'BMF']

    }

    relevant_years = {
        'external_matura_percentile': [2014, 2015, 2016, 2017],
        'scio_percentile': [2014, 2015, 2016, 2017],
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
        return redirect('/final')

    return render_template('admission_wavers.html', form=form, session=session)

@app.route('/final', methods=['GET'])
@login_required
@require_filled_form('admissions_wavers')
def final():
    return render_template('final.html', session=session)


@app.route('/submit_app')
@login_required
def submit_app():
    session['application_submitted'] = True
    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    app.application = flask.json.dumps(dict(session))
    app.submitted = True
    app.submitted_at = datetime.datetime.now()
    db.session.commit()

    flash('Gratulujeme, Vaša prihláška bola podaná!')
    return redirect(url_for('final'))

@app.route('/grades_control', methods=['GET'])
@login_required
def grades_control():
    rendered = render_template('grade_listing.html', session=session)
    # pdf = pdfkit.from_string(rendered, False)

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = 'inline; filename=grades_control.pdf'

    return rendered

@app.route('/application_form', methods=['GET'])
@login_required
def application_form():
    lists = {
        'sex': dict(SEX_CHOICES),
        'marital_status': dict(MARITAL_STATUS_CHOICES),
        'country': dict(COUNTRY_CHOICES),
        'city': dict(CITY_CHOICES),
        'highschool': dict(HIGHSCHOOL_CHOICES),
        'hs_study_programme': dict(HS_STUDY_PROGRAMME_CHOICES),
        'education_level': dict(EDUCATION_LEVEL_CHOICES),
        'study_programme': dict(STUDY_PROGRAMME_CHOICES)
    }

    app = ApplicationForm.query.filter_by(user_id=current_user.id).first()
    rendered = render_template('application_form.html', session=session,
                               lists=lists, id=app.id)

    return rendered


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)

                # set the index endpoint as already visited (in order for the
                # menu generation to work correctly)
                session['index'] = ''

                flash('Gratulujeme, boli ste prihlásení do prostredia ePrihlaska!')
                return redirect(url_for('study_programme'))
        flash('Nesprávne prihlasovacie údaje', 'error')

    return render_template('login.html', form=form, session=session)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_pass = generate_password_hash(form.password.data,
                                             method='sha256')

        new_user = User(email=form.email.data,
                        password=hashed_pass)
        db.session.add(new_user)
        db.session.commit()

        # pre-populate the email field in the form using the email provided at
        # signup time
        session['email'] = form.email.data

        new_application_form = ApplicationForm(user_id=new_user.id)
        db.session.add(new_application_form)
        db.session.commit()

        flash('Nový používateľ bol zaregistrovaný. Prosím, prihláste sa.')
        return redirect('/login')

    return render_template('signup.html', form=form, session=session)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    # Clear out the session
    keys = list(session.keys()).copy()
    for k in keys:
        session.pop(k)

    logout_user()
    return redirect(url_for('index'))

@app.route('/forgotten_password/<hash>', methods=['GET', 'POST'])
def forgotten_password_hash(hash):
    token = ForgottenPassworToken.query.filter_by(hash=hash).first()
    if token and token.valid:
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
            flash('Vaše heslo bolo zmenené')
            return redirect(url_for('login'))
        return render_template('forgotten_password.html', form=form)

    return redirect(url_for('index'))

@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    form = ForgottenPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            hash = str(uuid.uuid4())
            token = ForgottenPassworToken(hash=hash,
                                          user_id=user.id)
            db.session.add(token)
            db.session.commit()

            link = url_for('forgotten_password_hash', hash=hash, _external=True)
            msg = Message('ePrihlaska - zabudnuté heslo')
            msg.body = FORGOTTEN_PASSWORD_MAIL.format(link)
            msg.recipients = [user.email]
            mail.send(msg)

        flash('Ak bol poskytnutý e-mail nájdený, boli naň zaslané informácie o ďalšom postupe')

    return render_template('forgotten_password.html', form=form, session=session)


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

        new_application_form = ApplicationForm(user_id=user.id)
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
