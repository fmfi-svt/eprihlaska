import sys
import re
import flask.json
from flask import url_for
from aisikl.app import Application
import aisikl.portal
from fladgejt.login import create_client

from eprihlaska.consts import (
    PRIHLASKA_DEGREE,
    STUDY_PROGRAMME_BACHELORS,
    STUDY_PROGRAMME_MASTERS,
    STUDY_PROGRAMME_TYPES,
)


VSPK014 = "/ais/servlets/WebUIServlet?appClassName=ais.gui.vs.pk.VSPK014App&kodAplikacie=VSPK014&uiLang=SK"


def create_context(*, my_entity_id, andrvotr_api_key, andrvotr_authority_token, beta):
    server = dict(
        login_types=("saml_andrvotr",),
        ais_url=("https://ais2-beta.uniba.sk/" if beta else "https://ais2.uniba.sk/"),
    )
    params = dict(
        type="saml_andrvotr",
        my_entity_id=my_entity_id,
        andrvotr_api_key=andrvotr_api_key,
        andrvotr_authority_token=andrvotr_authority_token,
    )
    return create_client(server, params).context


def test_ais(ctx):
    # Open 'cierna skrynka'
    apps = aisikl.portal.get_apps(ctx)
    app, prev_ops = Application.open(ctx, apps["AS042"].url)

    # Open main dialog
    dlg = app.awaited_open_main_dialog([prev_ops[0]])
    # Open another selection dialog
    dlg = app.awaited_open_dialog([prev_ops[1]])

    # Select the last row in the table
    app.d.table.select(len(app.d.table.all_rows()) - 1)

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
    app.d.textTextArea.write(
        "Dobry den pani prodekanka, toto prosim ignorujte, len testujem ten nestastny AIS."
    )

    # Confirm the message
    with app.collect_operations() as ops:
        app.d.enterButton.click()


def check_application_exists(ctx, application_id, application_type) -> bool:
    note_url = url_for("admin_view", id=application_id, _external=True)

    app, prev_ops = Application.open(ctx, VSPK014)

    # Ocakavame, ze sa otvoria dve okna
    app.awaited_open_main_dialog([prev_ops[0]])
    app.awaited_open_dialog([prev_ops[1]])

    # Vyberieme prvy akademicky rok (ocakavane nasledujuci)
    app.d.akademickyRokComboBox.select(0)
    app.d.potvrditRokButton.click()

    app.d.poznamkaTextField.write(note_url)

    with app.collect_operations() as ops:
        app.d.enterButton.click()
    app.awaited_close_dialog(ops)

    # Nacital sa zoznam prihlasok.
    rows = app.d.ZoznamPodanychPrihlasokTable.all_rows()
    if not rows:
        return False

    for row in rows:
        note = row["poznamka"].split("\n")

        if note_url not in note:
            continue

        if f"typ:{application_type}" not in note:
            continue

        return True

    return False


class NoValidProgramme(Exception):
    pass


def save_application_form(
    ctx, application, lists, application_id, process_type
) -> tuple[str | None, dict]:
    types = [STUDY_PROGRAMME_BACHELORS, STUDY_PROGRAMME_MASTERS]
    ais2_output = None
    notes = {}
    created_some = False

    for type_ in types:
        try:
            this_process_type = process_type
            if process_type == "none" and created_some:
                # Ocakavame, ze pri druhej prihlaske bude clovek uz v AISe existovat, kedze sme ho vyrobili.
                process_type = "no_fill"

            this_ais2_output, this_notes = _save_application_form(
                ctx,
                application,
                lists,
                application_id,
                this_process_type,
                type_,
            )
            created_some = True
        except NoValidProgramme:
            continue

        if "person_exists" in this_notes:
            return this_ais2_output, this_notes

        notes.update(this_notes)
        if this_ais2_output:
            if ais2_output:
                ais2_output += (
                    "\n------------------------------------\n" + this_ais2_output
                )
            else:
                ais2_output = this_ais2_output

    return ais2_output, notes


def _save_application_form(
    ctx,
    application,
    lists,
    application_id,
    process_type,
    study_programme_type,
) -> tuple[str | None, dict]:
    session = flask.json.loads(application.application)
    notes = {}

    study_programmes = []
    for prog in session["study_programme"]:
        if prog == "_":
            continue
        if STUDY_PROGRAMME_TYPES[prog] != study_programme_type:
            continue
        study_programmes.append(prog)

    if not study_programmes:
        raise NoValidProgramme()

    if check_application_exists(ctx, application_id, study_programme_type):
        return None, {}

    app, prev_ops = Application.open(ctx, VSPK014)

    # Otvori sa dialog a v nom dalsi dialog
    dlg = app.awaited_open_main_dialog([prev_ops[0]])
    dlg = app.awaited_open_dialog([prev_ops[1]])

    # Vyberieme prvy akademicky rok (ocakavane nasledujuci)
    app.d.akademickyRokComboBox.select(0)
    app.d.potvrditRokButton.click()

    # Zavrieme filter
    with app.collect_operations() as ops:
        app.d.enterButton.click()
    dlg = app.awaited_close_dialog(ops)

    # Vyrobime novu prihlasku
    with app.collect_operations() as ops:
        app.d.novyButton.click()

    dlg = app.awaited_open_dialog(ops)

    # Opyta sa nas to na stupen studia
    selected_stupen = None
    for idx, option in enumerate(app.d.stupenComboBox.options):
        if option.id == PRIHLASKA_DEGREE[study_programme_type]:
            selected_stupen = idx
            break

    if not selected_stupen:
        raise Exception(
            f"Expected option {PRIHLASKA_DEGREE[study_programme_type]} in VSPK064 dialog, but not found."
        )

    app.d.stupenComboBox.select(selected_stupen)

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

    app.d.kodStatTextField.write(session["nationality"])

    with app.collect_operations() as ops:
        app.d.button3.click()

    # If the birth number is not filled in, just skip the whole "guess the
    # person by their birth number" part
    if len(session["birth_no"].strip()) != 0:
        app.d.rodneCisloTextField.write(session["birth_no"])

        # Click on relevant rodneCisloButton
        with app.collect_operations() as ops:
            app.d.rodneCisloButton.click()

        # FIXME: This i here is simply one nasty hack. Its purpose is simple:
        # we really do not know what sort of an op will AIS return. Thus, we'll
        # try openDialog and confirmBox and throw an exception otherwise
        while len(ops) != 0:
            # Close the dialog if some shows up
            if len(ops) == 1 and ops[0].method == "openDialog":
                app.awaited_open_dialog(ops)

                with app.collect_operations() as ops:
                    app.d.closeButton.click()

                app.awaited_close_dialog(ops)

                # Clear the ops
                ops = []

            # It may happen that a confirmBox gets shown (for whatever reason).
            # Should that happen, the confirmBox should be just closed.
            elif len(ops) == 1 and ops[0].method == "confirmBox":
                with app.collect_operations() as ops:
                    app.confirm_box(-1)

            elif len(ops) == 1:
                raise Exception("Unexpected ops {}".format(ops))

    # If the priezviskoTextField is not empty, it most probably means the
    # person is already registered in
    if app.d.priezviskoTextField.value != "" and process_type == "none":
        notes["person_exists"] = {
            "name": app.d.menoTextField.value,
            "surname": app.d.priezviskoTextField.value,
            "date_of_birth": app.d.datumNarodeniaDateControl.value,
            "place_of_birth": app.d.sklonovanieNarTextField.value,
            "phone": app.d.telefonTextField.value,
            "email": app.d.emailPrivateTextField.value,
        }
        # end the process here by returning
        return None, notes

    # Turn off automatic generation of ID numbers for applications.
    app.d.ecAutomatickyCheckBox.set_to(False)
    app.d.evidCisloNumberControl.write(str(application.id))

    # If we are in the 'no_fill' process_type, the personal data and address
    # should be taken from whatever AIS2 provides
    if process_type != "no_fill":
        app.d.menoTextField.write(session["basic_personal_data"]["name"])
        app.d.priezviskoTextField.write(session["basic_personal_data"]["surname"])
        if (
            session["basic_personal_data"]["surname"]
            != session["basic_personal_data"]["born_with_surname"]
        ):
            app.d.povPriezviskoTextField.write(
                session["basic_personal_data"]["born_with_surname"]
            )

        # This should basically never happen in production, but when testing,
        # it would be nice not to fail in case the application does not have
        # the submitted_at date filled in yet.
        if application.submitted_at is not None:
            app.d.datumOdoslaniaDateControl.write(
                application.submitted_at.strftime("%d.%m.%Y")
            )
        app.d.datumNarodeniaDateControl.write(session["date_of_birth"])

        # Sex selection
        if session["sex"] == "male":
            app.d.kodPohlavieRadioBox.select(0)
        else:
            app.d.kodPohlavieRadioBox.select(1)

        # rodinny_stav_text = lists['marital_status'][session['marital_status']].split(' - ')[0]
        ## FIXME: AIS2 hack
        # if rodinny_stav_text == 'nezistený':
        #    rodinny_stav_text = 'neurčené'

        # rodinny_stav_index = None
        # for idx, option in enumerate(app.d.kodRodinnyStavComboBox.options):
        #    option_text = option.title.split('/')[0].lower()
        #    if option_text == rodinny_stav_text:
        #        rodinny_stav_index = idx

        # if rodinny_stav_index is not None:
        #    app.d.kodRodinnyStavComboBox.select(rodinny_stav_index)

        # Clean up place of birth and state of birth
        with app.collect_operations() as ops:
            app.d.c30Button.click()
            app.d.c31Button.click()

        if session["country_of_birth"] == "703":
            place_of_birth_psc = lists["city_psc"][session["place_of_birth"]]
            select_city_by_psc_ciselnik_code(
                app,
                place_of_birth_psc,
                session["place_of_birth"],
                app.d.sklonovanieNarTextField,
                app.d.vyberMiestoNarodeniabutton,
            )
        else:
            app.d.statNarodeniaTextField.write(
                lists["country"][session["country_of_birth"]]
            )  # noqa
            with app.collect_operations() as ops:
                app.d.button22.click()

            app.d.sklonovanieNarTextField.write(session["place_of_birth_foreign"])  # noqa

        app.d.telefonTextField.write(session["phone"])
        app.d.emailPrivateTextField.write(session["email"])

        # Address
        fill_in_address("address_form", app, session, lists)

        # Correspondence address
        if session["has_correspondence_address"]:
            app.d.pouzitPSAdresuCheckBox.toggle()
            fill_in_address("correspondence_address", app, session, lists)

    programme_controls = [
        ("program1TextField", "button12", "c11Button"),
        ("program2TextField", "button13", "c12Button"),
        ("program3TextField", "button14", "c13Button"),
    ]

    for i, prog in enumerate(study_programmes):
        field, expand, confirm = programme_controls[i]

        # Vyplnime odbor
        getattr(app.d, field).write(prog)

        # Nechame doplnit cely nazov odboru
        with app.collect_operations() as ops:
            getattr(app.d, expand).click()

        print("After filling in study programme: {}".format(ops), file=sys.stderr)

        # Deal with the dialog that opens up when a prefix of a programme
        # matches various options, e.g. FYZ and FYZ/k
        choose_study_programme(app, ops, prog)

        # Nechame doplit povinne predmety
        with app.collect_operations() as ops:
            getattr(app.d, confirm).click()

    app.d.rokZaverSkuskyNumberControl.write(
        str(session["basic_personal_data"]["matura_year"])
    )

    if session["finished_highschool_check"] == "SK":
        # 'XXXXXXX' signifies "highschool not found"
        if session["studies_in_sr"]["highschool"] != "XXXXXXX":
            app.d.sSKodTextField.write(session["studies_in_sr"]["highschool"])
            app.d.button10.click()

        app.d.odborySkolyCheckBox.toggle()

        # 'XXXXXX' signifies 'study programme not found'
        if session["studies_in_sr"]["study_programme_code"] != "XXXXXX":
            app.d.kodOdborTextField.write(
                session["studies_in_sr"]["study_programme_code"]
            )
            app.d.c1Button.click()

        # Select correct option index based on education_level
        typ_vzdelania_index = None
        for idx, option in enumerate(app.d.sSKodTypVzdelaniaComboBox.options):
            if option.id == session["studies_in_sr"]["education_level"]:
                typ_vzdelania_index = idx

        if typ_vzdelania_index is not None:
            app.d.sSKodTypVzdelaniaComboBox.select(typ_vzdelania_index)

    else:
        # foreign high school
        app.d.sSKodTextField.write("999999999")
        app.d.button10.click()

        # študijný odbor na zahraničnej škole
        app.d.kodOdborTextField.write("0000500")

    # Remove all rows in vysvedceniaTable

    print("Final: {}".format(ops), file=sys.stderr)
    while len(app.d.vysvedceniaTable.all_rows()) > 0:
        with app.collect_operations() as ops:
            app.d.odobratButton.click()
        print("Removing: {}".format(ops), file=sys.stderr)
        # really confirm
        with app.collect_operations() as ops:
            app.confirm_box(2)

        if ops:
            rodne_cislo_dlg = app.awaited_open_dialog(ops)

            with app.collect_operations() as ops:
                app.d.closeButton.click()

            rodne_cislo_dlg = app.awaited_close_dialog([ops[0]])
            print("In dialog: {}".format(ops), file=sys.stderr)
            if len(ops) > 1:
                rodne_cislo_dlg = app.awaited_open_dialog([ops[1]])

                with app.collect_operations() as ops:
                    app.d.closeButton.click()

                print("after close: {}".format(ops), file=sys.stderr)
                rodne_cislo_dlg = app.awaited_close_dialog(ops)

        print("After confirm: {}".format(ops), file=sys.stderr)

    ABBRs, F = generate_subject_abbrevs(session)

    for abbr in ABBRs:
        add_subject(app, abbr)
        fill_in_table_cells(app, abbr, F, session)

    # Unselect everything in prilohyTable (literally)
    unselect_table(app.d.prilohyTable)
    checkboxes = generate_checkbox_abbrs(session)

    # Add dean's letter
    if (
        session["basic_personal_data"]["dean_invitation_letter"]
        and session["basic_personal_data"]["dean_invitation_letter_no"]
    ):
        checkboxes.add("ListD")

    competition_checkboxes_map = {
        "MAT": "OlymM",
        "FYZ": "OlymF",
        "INF": "OlymI",
        "BIO": "OlymB",
        "CHM": "OlymCH",
        "SOC_MAT": "SočM",
        "SOC_INF": "SočI",
        "SOC_BIO": "SočB",
        "SOC_CHM": "SočCH",
        "TMF": "TMF",
        "FVAT_MAT": "FVAT_M",
        "FVAT_FYZ": "FVAT_F",
        "FVAT_INF": "FVAT_I",
        "FVAT_BIO": "FVAT_B",
        "FVAT_CH": "FVAT_Ch",
        "ROBOCUP": "RoboCup",
        "IBOBOR": "iBobor",
        "ZENIT": "ZENIT",
        "TROJSTEN_KMS": "KMS",
        "TROJSTEN_FKS": "FKS",
        "TROJSTEN_KSP": "KSP",
    }

    # Add checkboxes based on competitions
    for s in ["competition_1", "competition_2", "competition_3"]:
        if s in session and session[s]["competition"] != "_":
            comp = session[s]["competition"]
            checkboxes.add(competition_checkboxes_map[comp])

            # TODO: "SVOC_MAT" currently means both SocM and SocF
            # This line is a simple band-aid at best and should be
            # refactored
            if comp == "SVOC_MAT":
                checkboxes.add("SočF")

    # Check those items in prilohyCheckList that have been generated from the
    # submitted application form (the code above)
    for idx, row in enumerate(app.d.prilohyTable.all_rows()):
        if row.cells[1].value in checkboxes:
            app.d.prilohyTable.edit_cell("checkBox", idx, True)

    # Prepare poznamka_text
    poznamka_items = []
    if "SCIO" in checkboxes:
        poznamka_items.append("SCIO")
    if "ExtMat" in checkboxes:
        poznamka_items.append("ExternaMaturitaMat")

    poznamka_items.append(url_for("admin_view", id=application_id, _external=True))
    poznamka_items.append(f"typ:{study_programme_type}")
    poznamka_text = "\n".join(poznamka_items)

    app.d.poznamkaTextArea.write(poznamka_text)

    # Submit the app
    with app.collect_operations() as ops:
        app.d.enterButton.click()

    print("Post submit: {}".format(ops), file=sys.stderr)

    # A set of confirm boxes may show up if highschool grades were filled in
    if len(ABBRs) > 0:
        ops = deal_with_confirm_boxes(app, ops, notes)

    errors = app.d.statusHtmlArea.content

    ops = deal_with_confirm_boxes(app, ops, notes)

    if len(ops) == 1 and ops[-1].method == "messageBox":
        if "existuje osoba s Vami zadaným emailom." in errors:
            email = app.d.emailPrivateTextField.value
            notes["email_exists"] = email
            app.d.emailPrivateTextField.write("")

        with app.collect_operations() as ops:
            app.d.enterButton.click()

        ops = deal_with_confirm_boxes(app, ops, notes)
    else:
        with app.collect_operations() as ops:
            app.d.enterButton.click()

    print("After messageBox: {}".format(ops), file=sys.stderr)
    errors = app.d.statusHtmlArea.content
    print("errors: {}".format(errors), file=sys.stderr)

    app.awaited_close_dialog(ops)
    return errors, notes


def deal_with_confirm_boxes(app, ops, notes):
    while ops and ops[-1].method == "confirmBox":
        if "evidenčným číslom" in ops[-1].args[0]:
            with app.collect_operations() as ops:
                # Generate new id number for the app
                app.confirm_box(-1)

                num = app.d.evidCisloNumberControl.bdvalue
                notes["app_id_exists"] = num

                app.d.evidCisloNumberControl.write("")
                app.d.ecAutomatickyCheckBox.toggle()

                app.d.enterButton.click()
        else:
            with app.collect_operations() as ops:
                app.confirm_box(2)
    return ops


def fill_in_address(field, app, session, lists):
    fields_map = {
        "city": [app.d.trIdObecTextField, app.d.psIdObecTextField],
        "city_button": [app.d.button4, app.d.button7],
        "posta": [app.d.trPostaTextField, app.d.psPostaTextField],
        "country_button": [app.d.button5, app.d.button8],
        "country": [app.d.trKodStatTextField, app.d.psKodStatTextField],
        "street": [app.d.trUlicaTextField, app.d.psUlicaTextField],
        "street_no": [
            app.d.trOrientacneCisloTextField,
            app.d.psOrientacneCisloTextField,
        ],
        "postal_no": [app.d.trPSCTextField, app.d.psPSCTextField],
    }

    if field == "address_form":
        fields = {k: v[0] for k, v in fields_map.items()}
    else:
        fields = {k: v[1] for k, v in fields_map.items()}

    if session[field]["country"] == "703":
        # Local (SR) address
        city = lists["city"][session[field]["city"]]
        city = re.sub(r",[^,]+$", "", city)
        city_parts = city.split(" ")
        city_psc = lists["city_psc"][session[field]["city"]]

        # First write country to the country field (even in case of SK)
        fields["country"].write(lists["country"][session[field]["country"]])
        with app.collect_operations() as ops:
            fields["country_button"].click()

        select_city_by_psc_ciselnik_code(
            app, city_psc, session[field]["city"], fields["city"], fields["city_button"]
        )

        # TODO: hack to work with current AIS
        # Write the actual city to "Post office" field
        fields["posta"].write(city)
    else:
        # Foreign (non SR) address
        fields["country"].write(lists["country"][session[field]["country"]])

        with app.collect_operations() as ops:
            fields["country_button"].click()

        fields["posta"].write(session[field]["city_foreign"])

    fields["street"].write(session[field]["street"])
    fields["street_no"].write(session[field]["street_no"])

    fields["postal_no"].write(session[field]["postal_no"][:10])


def add_to_set_on_grade_field(S, F, session, grade_field, abbr):
    if grade_field in session and "grade_first_year" in session[grade_field]:
        S.add(abbr)
        F.add(grade_field)


def add_to_set_on_further_study_info(S, F, session, field, abbr):
    if (
        "further_study_info" in session
        and field in session["further_study_info"]
        and session["further_study_info"][field]
    ):
        S.add(abbr)
        F.add(field)


def generate_subject_abbrevs(session):
    ABBRs = set()
    F = set()
    add_to_set_on_grade_field(ABBRs, F, session, "grades_mat", "M")
    add_to_set_on_grade_field(ABBRs, F, session, "grades_inf", "I")
    add_to_set_on_grade_field(ABBRs, F, session, "grades_fyz", "F")
    add_to_set_on_grade_field(ABBRs, F, session, "grades_bio", "B")
    add_to_set_on_grade_field(ABBRs, F, session, "grades_che", "CH")

    field_abbr_map = {
        "external_matura_percentile": "M",
        "scio_percentile": "IP",
        "scio_date": "IP",
        "matura_mat_grade": "M",
        "matura_fyz_grade": "F",
        "matura_inf_grade": "I",
        "matura_bio_grade": "B",
        "matura_che_grade": "CH",
        "will_take_mat_matura": "M",
        "will_take_fyz_matura": "F",
        "will_take_inf_matura": "I",
        "will_take_bio_matura": "B",
        "will_take_che_matura": "CH",
        "will_take_external_mat_matura": "M",
    }

    for field, abbr in field_abbr_map.items():
        add_to_set_on_further_study_info(ABBRs, F, session, field, abbr)
    return ABBRs, F


def generate_checkbox_abbrs(session):
    checkboxes = set()
    field_abbr_map = {
        "matura_mat_grade": "MatM",
        "matura_fyz_grade": "MatF",
        "matura_inf_grade": "MatI",
        "matura_bio_grade": "MatB",
        "matura_che_grade": "MatCh",
        "will_take_mat_matura": "MatM",
        "will_take_fyz_matura": "MatF",
        "will_take_inf_matura": "MatI",
        "will_take_che_matura": "MatCh",
        "will_take_bio_matura": "MatB",
        "will_take_external_mat_matura": "ExtMat",
        "will_take_scio": "SCIO",
    }
    for field, abbr in field_abbr_map.items():
        add_further_study_info_checkbox(checkboxes, session, field, abbr)
    return checkboxes


def add_further_study_info_checkbox(checkboxes, session, field, chkb):
    if (
        "further_study_info" in session
        and field in session["further_study_info"]
        and session["further_study_info"][field]
    ):
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

    # Add 'N' to subject level, if such a cell exists
    index = len(app.d.vysvedceniaTable.all_rows()) - 1
    try:
        app.d.vysvedceniaTable.edit_cell("kodUrovenMat", index, "N")
    except KeyError:
        pass


def fill_in_table_cells(app, abbr, F, session):
    if abbr == "M":
        if "external_matura_percentile" in F:
            p = session["further_study_info"]["external_matura_percentile"]
            index = len(app.d.vysvedceniaTable.all_rows()) - 1
            app.d.vysvedceniaTable.edit_cell("percentil", index, p)

        if "matura_mat_grade" in F:
            matura_grade_to_table_cell(app, session, "matura_mat_grade")

        if "grades_mat" in F:
            grades_to_table_cells(app, session, "grades_mat")

    if abbr == "F":
        if "matura_fyz_grade" in F:
            matura_grade_to_table_cell(app, session, "matura_fyz_grade")

        if "grades_fyz" in F:
            grades_to_table_cells(app, session, "grades_fyz")

    if abbr == "B":
        if "matura_bio_grade" in F:
            matura_grade_to_table_cell(app, session, "matura_bio_grade")

        if "grades_bio" in F:
            grades_to_table_cells(app, session, "grades_bio")

    if abbr == "CH":
        if "matura_che_grade" in F:
            matura_grade_to_table_cell(app, session, "matura_che_grade")

        if "grades_che" in F:
            grades_to_table_cells(app, session, "grades_che")

    if abbr == "I":
        if "matura_inf_grade" in F:
            matura_grade_to_table_cell(app, session, "matura_inf_grade")

        if "grades_inf" in F:
            grades_to_table_cells(app, session, "grades_inf")

    if abbr == "IP":
        if "scio_percentile" in F or "scio_date" in F:
            p = session["further_study_info"]["scio_percentile"]
            d = session["further_study_info"]["scio_date"]
            desc = "SCIO {}".format(d)
            index = len(app.d.vysvedceniaTable.all_rows()) - 1
            app.d.vysvedceniaTable.edit_cell("popis", index, desc)
            app.d.vysvedceniaTable.edit_cell("percentil", index, p)


def grades_to_table_cells(app, session, grades_field):
    first = session[grades_field]["grade_first_year"]
    second = session[grades_field]["grade_second_year"]
    third = session[grades_field]["grade_third_year"]
    index = len(app.d.vysvedceniaTable.all_rows()) - 1

    if first:
        app.d.vysvedceniaTable.edit_cell("znamkaI", index, first)
    if second:
        app.d.vysvedceniaTable.edit_cell("znamkaII", index, second)
    if third:
        app.d.vysvedceniaTable.edit_cell("znamkaIII", index, third)


def matura_grade_to_table_cell(app, session, grade_field):
    g = session["further_study_info"][grade_field]
    index = len(app.d.vysvedceniaTable.all_rows()) - 1
    app.d.vysvedceniaTable.edit_cell("znamkaMaturitna", index, g)


def unselect_table(table):
    """
    Unselect all first checkboxes in a table. Don't ask me why.
    """
    for idx, row in enumerate(table.all_rows()):
        table.edit_cell("checkBox", idx, False)


def unselect_checklist(checklist):
    for item in checklist.items:
        item.checked = False
    checklist._mark_changed()


def choose_study_programme(app, ops, study_programme):
    # Do nothing if there is no dialog to be opened
    if len(ops) == 0:
        return

    if len(ops) == 1 and ops[0].method == "openDialog":
        app.awaited_open_dialog(ops)

        rows = app.d.table.all_rows()
        row_index = None
        for idx, row in enumerate(rows):
            if row.cells[0].value == study_programme:
                row_index = idx

        # If we did find a row, let's select it
        if row_index is not None:
            app.d.table.select(row_index)
        else:
            raise Exception("Could not find {}".format(study_programme))

        with app.collect_operations() as ops:
            app.d.enterButton.click()

        app.awaited_close_dialog(ops)
    else:
        raise Exception("Unexpected ops: {}".format(ops))


def select_city_by_psc_ciselnik_code(
    app, city_psc, ciselnik_code, city_field, city_button
):
    # Write PSC instead of city name (TODO: hack to work with current AIS)
    city_field.write(city_psc)
    with app.collect_operations() as ops:
        city_button.click()

    if len(ops) == 0:
        return

    if len(ops) == 1 and ops[-1].method == "openDialog":
        # Open selection dialogue
        select_dlg = app.awaited_open_dialog(ops)

        rows = app.d.table.all_rows()

        # Let's try to find the correct row by checking the ciselnik_code
        row_index = None
        for idx, row in enumerate(rows):
            print(
                "ciselnik_code: {}, row_value: {}".format(
                    ciselnik_code, row.cells[0].value
                ),
                file=sys.stderr,
            )
            if row.cells[0].value == ciselnik_code:
                row_index = idx

        # If we did find a row, let's select it
        if row_index is not None:
            app.d.table.select(row_index)
        else:
            raise Exception("Could not find ciselnik_code {}".format(city_psc))

        with app.collect_operations() as ops:
            app.d.enterButton.click()

        # Close selection dialogue
        select_dlg = app.awaited_close_dialog(ops)
    else:
        raise Exception("Expected openDialog in select_city_by_psc_ciselnik_code")
