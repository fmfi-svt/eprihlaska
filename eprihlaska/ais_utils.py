import os
import sys
import re
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR + '/votr/')


from aisikl.context import Context
from aisikl.app import Application
import aisikl.portal
import flask.json

def create_context(cookies, origin='ais2-beta.uniba.sk'):
    ctx = Context({'AISAuth': 'a6c5dc686b2a3f9ee9df801fd37f581a',
                   'JSESSIONID': 'B14E400CEDD079BC1C1315B4EEE01104'},
                  ais_url='https://'+origin+'/')
    return ctx



def open_dialog(ctx):

    return app, dlg

def save_application_form(ctx, application, lists):
    session = flask.json.loads(application.application)

    apps = aisikl.portal.get_apps(ctx)
    app, prev_ops = Application.open(ctx, apps['VSPK014'].url)

    # Otvori sa dialog a v nom dalsi dialog
    dlg = app.awaited_open_main_dialog([prev_ops[0]])
    dlg = app.awaited_open_dialog([prev_ops[1]])

    # Zavrieme ten dalsi dialog
    with app.collect_operations() as ops:
        app.d.enterButton.click()
        dlg = app.awaited_close_dialog(ops)

    # Vyrobime novu prihlasku
    with app.collect_operations() as ops:
        app.d.novyButton.click()

    dlg = app.awaited_open_dialog(ops)

    # Opyta sa nas to na stupen studia
    app.d.stupenComboBox.select(0)

    with app.collect_operations() as ops:
        app.d.enterButton.click()

    # Zavreme prvy dialog a otvori sa nam novy
    dlg = app.awaited_close_dialog([ops[0]])
    dlg = app.awaited_open_dialog([ops[1]])

    ##########
    # Vyplname prihlasku
    ##########

    # Vymazeme obcianstvo
    with app.collect_operations() as ops:
        app.d.button16.click()

    app.d.kodStatTextField.write(session['nationality'])

    with app.collect_operations() as ops:
        app.d.button3.click()

    app.d.rodneCisloTextField.write(session['birth_no'])

    app.d.menoTextField.write(session['basic_personal_data']['name'])
    app.d.priezviskoTextField.write(session['basic_personal_data']['surname'])
    app.d.povPriezviskoTextField.write(session['basic_personal_data']['born_with_surname'])
    app.d.datumOdoslaniaDateControl.write(application.submitted_at.strftime('%d.%m.%Y'))
    app.d.datumNarodeniaDateControl.write(session['date_of_birth'])
    app.d.evidCisloNumberControl.write(str(application.id))

    # Sex selection
    # FIXME: Votr bug
####if session['sex'] == 'male':
####    app.d.kodPohlavieRadioBox.select(0)
####else:
####    app.d.kodPohlavieRadioBox.select(1)


    rodinny_stav_text = lists['marital_status'][session['marital_status']].split(' - ')[0]
    # FIXME: AIS2 hack
    if rodinny_stav_text == 'nezistený':
        rodinny_stav_text = 'neurčené'

    rodinny_stav_index = None
    for idx, option in enumerate(app.d.kodRodinnyStavComboBox.options):
        option_text = option.title.split('/')[0].lower()
        if option_text == rodinny_stav_text:
            rodinny_stav_index = idx

    if rodinny_stav_index is not None:
        app.d.kodRodinnyStavComboBox.select(rodinny_stav_index)

    with app.collect_operations() as ops:
        app.d.c30Button.click()
        app.d.c31Button.click()

    if session['country_of_birth'] == '703':
        app.d.sklonovanieNarTextField.write(session['place_of_birth'])

        with app.collect_operations() as ops:
            app.d.vyberMiestoNarodeniabutton.click()
    else:
        app.d.statNarodeniaTextField.write(lists['country'][session['country_of_birth']])
        with app.collect_operations() as ops:
            app.d.button22.click()

        app.d.sklonovanieNarTextField.write(session['place_of_birth_foreign'])

    app.d.telefonTextField.write(session['phone'])
    app.d.emailPrivateTextField.write(session['email'])

    app.d.menoMatkyTextField.write(session['mother_name']['name'])
    app.d.priezviskoMatkyTextField.write(session['mother_name']['surname'])
    app.d.povPriezviskoMatkyTextField.write(session['mother_name']['born_with_surname'])

    app.d.menoOtcaTextField.write(session['father_name']['name'])
    app.d.priezviskoOtcaTextField.write(session['father_name']['surname'])
    app.d.povPriezviskoOtcaTextField.write(session['father_name']['born_with_surname'])

    # Address
    fill_in_address('address_form', app, session, lists)

    # Correspondence address
    if session['has_correspondence_address']:
        app.d.pouzitPSAdresuCheckBox.toggle()
        fill_in_address('correspondence_address', app, session, lists)

    # Vyplnime prvy odbor
    app.d.program1TextField.write(session['study_programme'][0])

    # Nechame doplnit cely nazov odboru
    with app.collect_operations() as ops:
        app.d.button12.click()

    # Nechame doplit povinne predmety
    with app.collect_operations() as ops:
        app.d.c11Button.click()

    second_study_programme = None
    third_study_programme = None

    if session['study_programme'][2] != '_':
        third_study_programme = session['study_programme'][2]

    if session['study_programme'][1] == '_' and \
       session['study_programme'][2] != '_':
        second_study_programme = session['study_programme'][2]
        third_study_programme = '_'

    if session['study_programme'][1] != '_':
        second_study_programme = session['study_programme'][1]

    # Second study programme
    if second_study_programme is not None:
        app.d.program2TextField.write(second_study_programme)

        # Nechame doplnit cely nazov odboru
        with app.collect_operations() as ops:
            app.d.button13.click()

        # Nechame doplit povinne predmety
        with app.collect_operations() as ops:
            app.d.c12Button.click()

    # Third study programme
    if third_study_programme not in [None, '_']:
        app.d.program3TextField.write(third_study_programme)

        # Nechame doplnit cely nazov odboru
        with app.collect_operations() as ops:
            app.d.button14.click()

        # Nechame doplit povinne predmety
        with app.collect_operations() as ops:
            app.d.c13Button.click()

    app.d.rokZaverSkuskyNumberControl.write(str(session['basic_personal_data']['matura_year']))

    if session['finished_highschool_check'] == 'SK':
        if session['studies_in_sr']['highschool'] != 'XXXXXXX':
            app.d.sSKodTextField.write(session['studies_in_sr']['highschool'])
            app.d.button10.click()

        app.d.odborySkolyCheckBox.toggle()

        if session['studies_in_sr']['study_programme_code'] != 'XXXXXXX':
            app.d.kodOdborTextField.write(session['studies_in_sr']['study_programme_code'])
            app.d.c1Button.click()

        # Select correct option index based on education_level
        typ_vzdelania_index = None
        for idx, option in enumerate(app.d.sSKodTypVzdelaniaComboBox.options):
            if option.id == session['studies_in_sr']['education_level']:
                typ_vzdelania_index = idx

        if typ_vzdelania_index is not None:
            app.d.sSKodTypVzdelaniaComboBox.select(typ_vzdelania_index)

    else:
        app.d.sSKodTextField.write('999999999')

    with app.collect_operations() as ops:
        app.d.enterButton.click()

    errors = app.d.statusHtmlArea.content
    print(errors)
    print(ops)

    ops = deal_with_confirm_boxes(app, ops)

    if ops[-1].method == 'messageBox':
        if 'existuje osoba s Vami zadaným emailom.' in errors:
            app.d.emailPrivateTextField.write('')

        with app.collect_operations() as ops:
            app.d.enterButton.click()

        ops = deal_with_confirm_boxes(app, ops)

    print(ops)
    dlg = app.awaited_close_dialog(ops)


def deal_with_confirm_boxes(app, ops):
    while ops[-1].method == 'confirmBox':
        if 'evidenčným číslom' in ops[-1].args[0]:
            with app.collect_operations() as ops:
                # Generate new id number for the app
                app.confirm_box(-1)

                app.d.evidCisloNumberControl.write('')
                app.d.ecAutomatickyCheckBox.toggle()

                app.d.enterButton.click()
        else:
            with app.collect_operations() as ops:
                app.confirm_box(2)
    return ops

def fill_in_address(field, app, session, lists):
    fields_map = {
        'city': [app.d.trIdObecTextField, app.d.psIdObecTextField],
        'city_button': [app.d.button4, app.d.button7],
        'posta': [app.d.trPostaTextField, app.d.psPostaTextField],
        'country_button': [app.d.button5, app.d.button8],
        'country': [app.d.trKodStatTextField, app.d.psKodStatTextField],
        'street': [app.d.trUlicaTextField, app.d.psUlicaTextField],
        'street_no': [app.d.trOrientacneCisloTextField,
                      app.d.psOrientacneCisloTextField],
        'postal_no': [app.d.trPSCTextField, app.d.psPSCTextField]
    }

    if field == 'address_form':
        fields = {k:v[0] for k, v in fields_map.items()}
    else:
        fields = {k:v[1] for k, v in fields_map.items()}

    if session[field]['country'] == '703':
        # Local (SR) address
        city = lists['city'][session[field]['city']]
        city = re.sub(r',[^,]+$', '', city)
        city_parts = city.split(' ')
        city_psc = lists['city_psc'][session[field]['city']]

        fields['city'].write(city_parts[0])

        with app.collect_operations() as ops:
            fields['city_button'].click()

        # Open selection dialogue
        select_dlg = app.awaited_open_dialog(ops)

        rows = app.d.table.all_rows()

        # Let's try to find the correct row by checking the PSC
        row_index = None
        for idx, row in enumerate(rows):
            if row.cells[1].value == city_psc:
                row_index = idx

        # If we did find a row, let's select it
        if row_index is not None:
            app.d.table.select(row_index)

        with app.collect_operations() as ops:
            app.d.enterButton.click()

        # Close selection dialogue
        select_dlg = app.awaited_close_dialog(ops)

        fields['posta'].write('')
    else:
        # Foreign (non SR) address
        fields['country'].write(lists['country'][session[field]['country']])

        with app.collect_operations() as ops:
            fields['country_button'].click()

        fields['posta'].write(session[field]['city_foreign'])

    fields['street'].write(session[field]['street'])
    fields['street_no'].write(session[field]['street_no'])

    fields['postal_no'].write(session[field]['postal_no'])
