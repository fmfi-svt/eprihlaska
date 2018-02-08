import os
import sys
import re
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR + '/votr/')


from aisikl.context import Context
from aisikl.app import Application
import aisikl.portal
import flask.json
from flask import url_for

def create_context(cookies, origin='ais2-beta.uniba.sk'):
    ctx = Context(cookies, ais_url='https://'+origin+'/')
    return ctx

def test_ais(ctx):
    # Open 'cierna skrynka'
    apps = aisikl.portal.get_apps(ctx)
    app, prev_ops = Application.open(ctx, apps['AS042'].url)

    # Open main dialog
    dlg = app.awaited_open_main_dialog([prev_ops[0]])
    # Open another selection dialog
    dlg = app.awaited_open_dialog([prev_ops[1]])

    # Select the last row in the table
    app.d.table.select(len(app.d.table.all_rows()) -1)

    # Click confirm (closes the dialog)
    with app.collect_operations() as ops:
        app.d.enterButton.click()
    dlg = app.awaited_close_dialog(ops)

    # Click on pridatPrispevokButton
    with app.collect_operations() as ops:
        app.d.pridatPrispevokButton.click()

    # Opens a dialog
    dlg = app.awaited_open_dialog(ops)
    # Write a short message
    app.d.textTextArea.write('Dobry den pani prodekanka, toto prosim ignorujte, len testujem ten nestastny AIS.')

    # Confirm the message
    with app.collect_operations() as ops:
        app.d.enterButton.click()

def save_application_form(ctx, application, lists, application_id, process_type):
    session = flask.json.loads(application.application)

    notes = {}

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

    # Click on relevant rodneCisloButton
    with app.collect_operations() as ops:
        app.d.rodneCisloButton.click()


    # It may happen that a confirmBox gets shown (for whatever reason).
    # Should that happen, the confirmBox should be just closed.
    if ops and ops[-1].method == 'confirmBox':
        app.confirm_box(-1)

    # Close the dialog if some shows up
    if ops and ops[-1].method == 'openDialog':
        rodne_cislo_dlg = app.awaited_open_dialog(ops)

        with app.collect_operations() as ops:
            app.d.closeButton.click()

        rodne_cislo_dlg = app.awaited_close_dialog(ops)

    # If the priezviskoTextField is not empty, it most probably means the
    # person is already registered in
    if app.d.priezviskoTextField.value != '' and process_type is None:
        notes['person_exists'] = {
            'name': app.d.menoTextField.value,
            'surname': app.d.priezviskoTextField.value,
            'date_of_birth': app.d.datumNarodeniaDateControl.value,
            'place_of_birth': app.d.sklonovanieNarTextField.value,
            'phone': app.d.telefonTextField.value,
            'email': app.d.emailPrivateTextField.value
        }
        # end the process here by returning
        return None, notes

    app.d.evidCisloNumberControl.write(str(application.id))

    # If we are in the 'no_fill' process_type, the personal data and address
    # should be taken from whatever AIS2 provides
    if process_type != 'no_fill':
        app.d.menoTextField.write(session['basic_personal_data']['name'])
        app.d.priezviskoTextField.write(session['basic_personal_data']['surname'])
        if session['basic_personal_data']['surname'] != session['basic_personal_data']['born_with_surname']:
            app.d.povPriezviskoTextField.write(session['basic_personal_data']['born_with_surname'])
        app.d.datumOdoslaniaDateControl.write(application.submitted_at.strftime('%d.%m.%Y'))
        app.d.datumNarodeniaDateControl.write(session['date_of_birth'])

        # Sex selection
        if session['sex'] == 'male':
            app.d.kodPohlavieRadioBox.select(0)
        else:
            app.d.kodPohlavieRadioBox.select(1)


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
        # 'XXXXXXX' signifies "highschool not found"
        if session['studies_in_sr']['highschool'] != 'XXXXXXX':
            app.d.sSKodTextField.write(session['studies_in_sr']['highschool'])
            app.d.button10.click()

        app.d.odborySkolyCheckBox.toggle()

        # 'XXXXXX' signifies 'study programme not found'
        if session['studies_in_sr']['study_programme_code'] != 'XXXXXX':
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
        # foreign high school
        app.d.sSKodTextField.write('999999999')
        app.d.button10.click()

        # študijný odbor na zahraničnej škole
        app.d.kodOdborTextField.write('0000500')

    #if 'grades_mat' in session and 'grade_first_year' in session['grades_mat']
    # Remove all rows in vysvedceniaTable
    while len(app.d.vysvedceniaTable.all_rows()) > 0:
        with app.collect_operations() as ops:
            app.d.odobratButton.click()
        # really confirm
        app.confirm_box(2)

    ABBRs, F = generate_subject_abbrevs(session)

    for abbr in ABBRs:
        add_subject(app, abbr)
        fill_in_table_cells(app, abbr, F, session)

    # Unselect everything in prilohyCheckList
    unselect_checklist(app.d.prilohyCheckList)
    checkboxes = generate_checkbox_abbrs(session)

    # Add dean's letter
    if session['basic_personal_data']['dean_invitation_letter'] and\
       session['basic_personal_data']['dean_invitation_letter_no']:
        checkboxes.add('ListD')

    competition_checkboxes_map = {
        'MAT': 'OlymM',
        'FYZ': 'OlymF',
        'INF': 'OlymI',
        'BIO': 'OlymB',
        'CHM': 'OlymCH',
        'SVOC_MAT': 'SočM',
        'SVOC_INF': 'SočI',
        'SVOC_BIO': 'SočB',
        'SVOC_CHM': 'SočCH',
        'TMF': 'TMF'
    }

    # Add checkboxes based on competitions
    for s in ['competition_1', 'competition_2', 'competition_3']:
        if s in session and session[s]['competition'] != '_':
            comp =  session[s]['competition']
            checkboxes.add(competition_checkboxes_map[comp])

            # TODO: "SVOC_MAT" currently means both SocM and SocF
            # This line is a simple band-aid at best and should be
            # refactored
            if comp == 'SVOC_MAT':
                checkboxes.add('SočF')


    # Check those items in prilohyCheckList that have been generated from the
    # submitted application form (the code above)
    for item in app.d.prilohyCheckList.items:
        if item.sid in checkboxes:
            item.checked = True
    app.d.prilohyCheckList._mark_changed()

    # Prepare poznamka_text
    poznamka_items = []
    if 'SCIO' in checkboxes:
        poznamka_items.append('SCIO')
    if 'ExtMat' in checkboxes:
        poznamka_items.append('ExternaMaturitaMat')
    poznamka_items.append(url_for('admin_view', id=application_id, _external=True))
    poznamka_text = '\n'.join(poznamka_items)

    app.d.poznamkaTextArea.write(poznamka_text)

    # Submit the app
    with app.collect_operations() as ops:
        app.d.enterButton.click()

    # A set of confirm boxes may show up if highschool grades were filled in
    if len(ABBRs) > 0:
        ops = deal_with_confirm_boxes(app, ops, notes)

    errors = app.d.statusHtmlArea.content

    ops = deal_with_confirm_boxes(app, ops, notes)

    if ops[-1].method == 'messageBox':
        if 'existuje osoba s Vami zadaným emailom.' in errors:
            email = app.d.emailPrivateTextField.value
            notes['email_exists'] = email
            app.d.emailPrivateTextField.write('')

        with app.collect_operations() as ops:
            app.d.enterButton.click()

        ops = deal_with_confirm_boxes(app, ops, notes)

    errors = app.d.statusHtmlArea.content

    dlg = app.awaited_close_dialog(ops)
    return errors, notes


def deal_with_confirm_boxes(app, ops, notes):
    while ops[-1].method == 'confirmBox':
        if 'evidenčným číslom' in ops[-1].args[0]:
            with app.collect_operations() as ops:
                # Generate new id number for the app
                app.confirm_box(-1)

                num = app.d.evidCisloNumberControl.bdvalue
                notes['app_id_exists'] = num

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

        if ops and ops[-1].method == 'openDialog':
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


def add_to_set_on_grade_field(S, F, session, grade_field, abbr):
    if grade_field in session and 'grade_first_year' in session[grade_field]:
        S.add(abbr)
        F.add(grade_field)

def add_to_set_on_further_study_info(S, F, session, field, abbr):
    if 'further_study_info' in session and \
       field in session['further_study_info'] and \
       session['further_study_info'][field]:
        S.add(abbr)
        F.add(field)

def generate_subject_abbrevs(session):
    ABBRs = set()
    F = set()
    add_to_set_on_grade_field(ABBRs, F, session, 'grades_mat', 'M')
    add_to_set_on_grade_field(ABBRs, F, session, 'grades_fyz', 'F')
    add_to_set_on_grade_field(ABBRs, F, session, 'grades_bio', 'B')

    field_abbr_map = {
        'external_matura_percentile': 'M',
        'scio_percentile': 'IP',
        'scio_date': 'IP',
        'matura_mat_grade': 'M',
        'matura_fyz_grade': 'F',
        'matura_inf_grade': 'I',
        'matura_bio_grade': 'B',
        'matura_che_grade': 'CH',
        'will_take_mat_matura': 'M',
        'will_take_fyz_matura': 'F',
        'will_take_inf_matura': 'I',
        'will_take_bio_matura': 'B',
        'will_take_che_matura': 'CH',
        'will_take_external_mat_matura': 'M'
    }

    for field, abbr in field_abbr_map.items():
        add_to_set_on_further_study_info(ABBRs, F, session,
                                         field, abbr)
    return ABBRs, F

def generate_checkbox_abbrs(session):
    checkboxes = set()
    field_abbr_map = {
        'will_take_mat_matura': 'MatM',
        'will_take_fyz_matura': 'MatF',
        'will_take_inf_matura': 'MatI',
        'will_take_che_matura': 'MatCh',
        'will_take_bio_matura': 'MatB',
        'will_take_external_mat_matura': 'ExtMat',
        'will_take_scio': 'SCIO'
    }
    for field, abbr in field_abbr_map.items():
        add_further_study_info_checkbox(checkboxes, session,
                                        field, abbr)
    return checkboxes

def add_further_study_info_checkbox(checkboxes, session,
                                    field, chkb):
    if 'further_study_info' in session and \
       field in session['further_study_info'] and \
       session['further_study_info'][field]:
        checkboxes.add(chkb)

def add_subject(app, abbr):
    # Add new rows (subjects)
    with app.collect_operations() as ops:
        app.d.novyButton.click()

    select_predmet_dlg = app.awaited_open_dialog(ops)

    rows = app.d.table.all_rows()
    row_index = None
    for idx, row in enumerate(rows):
        if row.cells[4].value == abbr:
            row_index = idx

    if row_index:
        app.d.table.select(row_index)

    # Submit the dialog
    with app.collect_operations() as ops:
        app.d.enterButton.click()

    select_predmet_dlg = app.awaited_close_dialog(ops)

def fill_in_table_cells(app, abbr, F, session):
    if abbr == 'M':
        if 'external_matura_percentile' in F:
            p = session['further_study_info']['external_matura_percentile']
            index = len(app.d.vysvedceniaTable.all_rows()) - 1
            app.d.vysvedceniaTable.edit_cell('percentil', index, p)

        if 'matura_mat_grade' in F:
            matura_grade_to_table_cell(app, session, 'matura_mat_grade')

        if 'grades_mat' in F:
            grades_to_table_cells(app, session, 'grades_mat')

    if abbr == 'F':
        if 'matura_fyz_grade' in F:
            matura_grade_to_table_cell(app, session, 'matura_fyz_grade')

        if 'grades_fyz' in F:
            grades_to_table_cells(app, session, 'grades_fyz')

    if abbr == 'B':
        if 'matura_bio_grade' in F:
            matura_grade_to_table_cell(app, session, 'matura_bio_grade')

        if 'grades_bio' in F:
            grades_to_table_cells(app, session, 'grades_bio')

    if abbr == 'CH':
        if 'matura_che_grade' in F:
            matura_grade_to_table_cell(app, session, 'matura_che_grade')

    if abbr == 'I':
        if 'matura_inf_grade' in F:
            matura_grade_to_table_cell(app, session, 'matura_inf_grade')

    if abbr == 'IP':
        if 'scio_percentile' in F or 'scio_date' in F:
            p = session['further_study_info']['scio_percentile']
            d = session['further_study_info']['scio_date']
            desc = 'SCIO {}'.format(d)
            index = len(app.d.vysvedceniaTable.all_rows()) - 1
            app.d.vysvedceniaTable.edit_cell('popis', index, desc)
            app.d.vysvedceniaTable.edit_cell('percentil', index, p)


def grades_to_table_cells(app, session, grades_field):
    first = session[grades_field]['grade_first_year']
    second = session[grades_field]['grade_second_year']
    third = session[grades_field]['grade_third_year']
    index = len(app.d.vysvedceniaTable.all_rows()) - 1

    if first:
        app.d.vysvedceniaTable.edit_cell('znamkaI', index, first)
    if second:
        app.d.vysvedceniaTable.edit_cell('znamkaII', index, second)
    if third:
        app.d.vysvedceniaTable.edit_cell('znamkaIII', index, third)

def matura_grade_to_table_cell(app, session, grade_field):
    g = session['further_study_info'][grade_field]
    index = len(app.d.vysvedceniaTable.all_rows()) - 1
    app.d.vysvedceniaTable.edit_cell('znamkaMaturitna', index, g)


def unselect_checklist(checklist):
    for item in checklist.items:
        item.checked = False
    checklist._mark_changed()
