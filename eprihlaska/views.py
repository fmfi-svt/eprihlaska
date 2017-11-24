from flask import render_template, flash, redirect, session
from eprihlaska import app
from eprihlaska.forms import (StudyProgrammeForm, BasicPersonalDataForm,
                              FurtherPersonalDataForm, AddressForm)
from munch import munchify

@app.route('/', methods=('GET', 'POST'))
def index():
    form = StudyProgrammeForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        flash('Vaše dáta boli uložené!')
        return redirect('/personal_info')
    return render_template('study_programme.html', form=form)


@app.route('/personal_info', methods=('GET', 'POST'))
def personal_info():
    form = BasicPersonalDataForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        flash('Vaše dáta boli uložené!')
        return redirect('/further_personal_info')
    return render_template('personal_info.html', form=form)

@app.route('/further_personal_info', methods=('GET', 'POST'))
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
    return render_template('further_personal_info.html', form=form)

@app.route('/address', methods=('GET', 'POST'))
def address():
    form = AddressForm(obj=munchify(dict(session)))
    if form.validate_on_submit():
        for k in form.data:
            session[k] = form.data[k]
        return redirect('/success')
    return render_template('address.html', form=form)

