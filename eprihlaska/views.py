from flask import (render_template, flash, redirect, session, request, url_for,
                   make_response)
from eprihlaska import app
from eprihlaska.forms import (StudyProgrammeForm, BasicPersonalDataForm,
                              FurtherPersonalDataForm, AddressForm,
                              PreviousStudiesForm, AdmissionWaversForm)
from munch import munchify
from functools import wraps

from .consts import MENU

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

@app.route('/', methods=('GET', 'POST'))
def index():
    form = StudyProgrammeForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        flash('Vaše dáta boli uložené!')
        return redirect('/personal_info')
    return render_template('study_programme.html', form=form, session=session)


@app.route('/personal_info', methods=('GET', 'POST'))
@require_filled_form('index')
def personal_info():
    form = BasicPersonalDataForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        flash('Vaše dáta boli uložené!')
        return redirect('/further_personal_info')
    return render_template('personal_info.html', form=form, session=session)

@app.route('/further_personal_info', methods=('GET', 'POST'))
@require_filled_form('personal_info')
def further_personal_info():
    form = FurtherPersonalDataForm(obj=munchify(dict(session)))

    # Do not show `birth_no` field if the user does not come from SK/CZ.
    # Do show it, however, if the user did not fill in their nationality yet.
    if session.get('nationality') not in ['703', '203', None]:
        form['basic_personal_data'].__delitem__('birth_no')

    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        flash('Vaše dáta boli uložené!')
        return redirect('/address')
    return render_template('further_personal_info.html', form=form,
                           session=session)

@app.route('/address', methods=('GET', 'POST'))
@require_filled_form('further_personal_info')
def address():
    form = AddressForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        flash('Vaše dáta boli uložené!')
        return redirect('/previous_studies')
    return render_template('address.html', form=form, session=session)

@app.route('/previous_studies', methods=('GET', 'POST'))
@require_filled_form('address')
def previous_studies():
    form = PreviousStudiesForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
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
        'TMF': ['BMF', 'FYZ', 'OZE', 'upFYIN', 'upMAFY']
    }

    for comp, desc in competition_list:
        if comp in ['MAT', 'SVOC_MAT'] and 'upINAN' not in study_programme_list:
            result_list.append((comp, desc))

        for c, sp_list in constraints.items():
            if comp == c and set(sp_list) & set(study_programme_list):
                result_list.append((comp, desc))
    return result_list

@app.route('/admissions_wavers', methods=('GET', 'POST'))
@require_filled_form('previous_studies')
def admissions_wavers():
    form = AdmissionWaversForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        return redirect('/final')


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
    for k, v in grade_constraints.items():
        if not study_programme_set & set(v) or \
           session['matura_year'] not in [2015, 2016, 2017, 2018]:
            form.__delitem__(k)

    for k, v in further_study_info_constraints.items():
        if not study_programme_set & set(v):
            if k in form['further_study_info']._fields:
                form['further_study_info'].__delitem__(k)

    for k, v in relevant_years.items():
        if not session['matura_year'] in v:
            if k in form['further_study_info']._fields:
                form['further_study_info'].__delitem__(k)

    return render_template('admission_wavers.html', form=form, session=session)

@app.route('/final', methods=['GET'])
@require_filled_form('admissions_wavers')
def final():
    return render_template('final.html', session=session)

@app.route('/grades_control', methods=['GET'])
def grades_control():
    rendered = render_template('grade_listing.html', session=session)
    # pdf = pdfkit.from_string(rendered, False)

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = 'inline; filename=grades_control.pdf'

    return rendered

