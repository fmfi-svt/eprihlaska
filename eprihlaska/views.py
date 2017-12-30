from flask import (render_template, flash, redirect, session, request, url_for,
                   make_response)
import flask.json
from eprihlaska import app, db
from eprihlaska.forms import (StudyProgrammeForm, BasicPersonalDataForm,
                              FurtherPersonalDataForm, AddressForm,
                              PreviousStudiesForm, AdmissionWaversForm,
                              LoginForm, SignupForm)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from authlib.client.apps import google

from munch import munchify
from functools import wraps

from .models import User, ApplicationForm, TokenModel
from .consts import MENU, STUDY_PROGRAMME_CHOICES
STUDY_PROGRAMMES = list(map(lambda x: x[0], STUDY_PROGRAMME_CHOICES))


def require_filled_form(form_key):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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

    form = StudyProgrammeForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        save_form(form)

        # Save study programmes into a list
        study_programme = []
        for sp in ['study_programme_1', 'study_programme_2',
                   'study_programme_3']:
            study_programme.append(session['study_programme_data'][sp])
        session['study_programme'] = study_programme

        flash('Vaše dáta boli uložené!')
        return redirect('/personal_info')
    return render_template('study_programme.html', form=form, session=session)


@app.route('/personal_info', methods=('GET', 'POST'))
@login_required
@require_filled_form('index')
def personal_info():
    form = BasicPersonalDataForm(obj=munchify(dict(session)))
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

    sp_data = session['study_programme_data']
    if sp_data['dean_invitation_letter'] and sp_data['dean_invitation_letter_no'] is not None:
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
    matura_year = session['study_programme_data']['matura_year']
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
        save_form(form)

        return redirect('/final')

    return render_template('admission_wavers.html', form=form, session=session)

@app.route('/final', methods=['GET'])
@login_required
@require_filled_form('admissions_wavers')
def final():

    return render_template('final.html', session=session)

@app.route('/grades_control', methods=['GET'])
@login_required
def grades_control():
    rendered = render_template('grade_listing.html', session=session)
    # pdf = pdfkit.from_string(rendered, False)

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = 'inline; filename=grades_control.pdf'

    return rendered

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
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

@app.route('/google/login', methods=['GET'])
def google_login():
    callback_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(callback_uri)

@app.route('/google/auth', methods=['GET'])
def google_authorize():
    token = google.authorize_access_token()
    profile = google.parse_openid(token)

    user = User.query.filter_by(email=profile.email).first()
    if not user:
        user = User(email=profile.email)
        db.session.add(user)
        db.session.commit()

        # pre-populate the email field in the form using the email obtained
        # from Google
        session['email'] = profile.email
        session['first_personal_data'] = {}
        session['first_personal_data']['name'] = profile.data['given_name']
        session['first_personal_data']['surname'] = profile.data['family_name']

        new_application_form = ApplicationForm(user_id=user.id)
        db.session.add(new_application_form)
        db.session.commit()

    login_user(user, remember=True)
    TokenModel.save('google', token, user)
    return redirect(url_for('study_programme'))
