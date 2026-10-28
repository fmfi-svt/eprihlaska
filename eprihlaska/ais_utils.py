import sys
import re
from collections.abc import Mapping
from abc import ABC
from typing import Any, Literal, NotRequired, TypedDict

import flask.json
from aisikl.app import Application
from aisikl.components.button import Button
from aisikl.components.checkbox import CheckBox
from aisikl.components.combobox import ComboBox
from aisikl.components.datecontrol import DateControl
from aisikl.components.htmlarea import HtmlArea
from aisikl.components.numbercontrol import NumberControl
from aisikl.components.radiobox import RadioBox
from aisikl.components.table import Table
from aisikl.components.textarea import TextArea
from aisikl.components.textfield import TextField
from aisikl.context import Context
from aisikl.dialog import Dialog
from aisikl.operations import (
    CloseDialogOp,
    ConfirmBoxOp,
    MessageBoxOp,
    OpenDialogOp,
    Operations,
)
from fladgejt.login import ServerDict, ParamsDictSamlAndrvotr, create_client

from eprihlaska.consts import (
    MASTERS_ID_OFFSET,
    PRIHLASKA_DEGREE,
    STUDY_PROGRAMME_BACHELORS,
    STUDY_PROGRAMME_MASTERS,
    STUDY_PROGRAMME_TYPES,
)
from eprihlaska.models import ApplicationForm


AS042 = "/ais/servlets/WebUIServlet?appClassName=ais.gui.as.forum.AS042App&kodAplikacie=AS042&uiLang=SK"
VSPK014 = "/ais/servlets/WebUIServlet?appClassName=ais.gui.vs.pk.VSPK014App&kodAplikacie=VSPK014&uiLang=SK"


class DiskusiaKTemeDialogsType(ABC, Dialog):
    enterButton: Button
    pridatPrispevokButton: Button
    table: Table
    textTextArea: TextArea


class EvidenciaUchadzacovPrihlasokDialogsType(ABC, Dialog):
    ZoznamPodanychPrihlasokTable: Table
    akademickyRokComboBox: ComboBox
    button10: Button
    button12: Button
    button13: Button
    button14: Button
    button16: Button
    button22: Button
    button3: Button
    button4: Button
    button5: Button
    button7: Button
    button8: Button
    c11Button: Button
    c12Button: Button
    c13Button: Button
    c1Button: Button
    c30Button: Button
    c31Button: Button
    closeButton: Button
    datumNarodeniaDateControl: DateControl
    datumOdoslaniaDateControl: DateControl
    ecAutomatickyCheckBox: CheckBox
    emailPrivateTextField: TextField
    enterButton: Button
    evidCisloNumberControl: NumberControl
    kodOdborTextField: TextField
    kodPohlavieRadioBox: RadioBox
    kodStatTextField: TextField
    menoTextField: TextField
    novyButton: Button
    odborySkolyCheckBox: CheckBox
    odobratButton: Button
    potvrditRokButton: Button
    pouzitPSAdresuCheckBox: CheckBox
    povPriezviskoTextField: TextField
    poznamkaTextArea: TextArea
    poznamkaTextField: TextField
    priezviskoTextField: TextField
    prilohyTable: Table
    program1TextField: TextField
    program2TextField: TextField
    program3TextField: TextField
    psIdObecTextField: TextField
    psKodStatTextField: TextField
    psOrientacneCisloTextField: TextField
    psPSCTextField: TextField
    psPostaTextField: TextField
    psUlicaTextField: TextField
    rodneCisloButton: Button
    rodneCisloTextField: TextField
    rokZaverSkuskyNumberControl: NumberControl
    sSKodTextField: TextField
    sSKodTypVzdelaniaComboBox: ComboBox
    sklonovanieNarTextField: TextField
    statNarodeniaTextField: TextField
    statusHtmlArea: HtmlArea
    stupenComboBox: ComboBox
    table: Table
    telefonTextField: TextField
    trIdObecTextField: TextField
    trKodStatTextField: TextField
    trOrientacneCisloTextField: TextField
    trPSCTextField: TextField
    trPostaTextField: TextField
    trUlicaTextField: TextField
    vyberMiestoNarodeniabutton: Button
    vysvedceniaTable: Table


class NotesDict(TypedDict):
    app_id_exists: NotRequired[str | None]
    application_exists: NotRequired[Literal[True]]
    email_exists: NotRequired[str]
    person_exists: NotRequired[Mapping[str, str]]


type SessionDict = Any  # ¯\_(ツ)_/¯


async def create_context(
    *,
    my_entity_id: str,
    andrvotr_api_key: str,
    andrvotr_authority_token: str,
    beta: bool,
) -> Context:
    server = ServerDict(
        login_types=("saml_andrvotr",),
        ais_url=("https://ais2-beta.uniba.sk/" if beta else "https://ais2.uniba.sk/"),
    )
    params = ParamsDictSamlAndrvotr(
        type="saml_andrvotr",
        my_entity_id=my_entity_id,
        andrvotr_api_key=andrvotr_api_key,
        andrvotr_authority_token=andrvotr_authority_token,
    )
    client = await create_client(server, params)
    return client.context


async def test_ais(ctx: Context) -> None:
    # Open 'cierna skrynka'
    app, ops = await Application[DiskusiaKTemeDialogsType].open(ctx, AS042)
    op1, op2 = ops.expect_two(OpenDialogOp, OpenDialogOp)
    await op1.perform()
    await op2.perform()

    # Select the last row in the table
    await app.d.table.select(len(await app.d.table.all_rows()) - 1)

    # Click confirm (closes the dialog)
    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()

    # Click on pridatPrispevokButton (opens a dialog)
    ops = await app.d.pridatPrispevokButton.click(return_ops=True)
    await ops.expect_one(OpenDialogOp).perform()

    # Write a short message
    await app.d.textTextArea.write(
        "Dobry den pani prodekanka, toto prosim ignorujte, len testujem ten nestastny AIS."
    )

    # Confirm the message
    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()


async def check_application_exists(
    ctx: Context, application_id: str, application_type: str
) -> bool:
    expected_note = f"EP#{application_id}{application_type}"

    app, ops = await Application[EvidenciaUchadzacovPrihlasokDialogsType].open(
        ctx, VSPK014
    )

    # Ocakavame, ze sa otvoria dve okna
    op1, op2 = ops.expect_two(OpenDialogOp, OpenDialogOp)
    await op1.perform()
    await op2.perform()

    # Vyberieme prvy akademicky rok (ocakavane nasledujuci)
    await app.d.akademickyRokComboBox.select(0)
    await app.d.potvrditRokButton.click()

    await app.d.poznamkaTextField.write(expected_note)

    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()

    # Nacital sa zoznam prihlasok.
    rows = await app.d.ZoznamPodanychPrihlasokTable.all_rows()
    await app.force_close()
    if not rows:
        return False

    for row in rows:
        note = row["poznamka"].split()

        if expected_note not in note:
            continue

        return True

    return False


class NoValidProgramme(Exception):
    pass


async def save_application_form(
    ctx: Context,
    application: ApplicationForm,
    lists: Mapping[str, Mapping[str, str]],
    application_id: str,
    process_type: Literal["none", "fill", "no_fill"],
) -> tuple[str | None, NotesDict]:
    session = flask.json.loads(application.application)

    types = [STUDY_PROGRAMME_BACHELORS, STUDY_PROGRAMME_MASTERS]
    ais2_output = None
    notes = NotesDict()
    created_some = False

    has_birth_no = len(session["birth_no"].strip()) != 0

    for type_ in types:
        try:
            this_ais2_output, this_notes = await _save_application_form(
                ctx,
                application,
                lists,
                application_id,
                process_type
                if not created_some or not has_birth_no
                else "no_fill",  # Ocakavame, ze pri druhej prihlaske bude clovek uz v AISe existovat, kedze sme ho vyrobili. Okrem ludi bez RC, tych vzdy vyrabame rovnako.
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


async def _save_application_form(
    ctx: Context,
    application: ApplicationForm,
    lists: Mapping[str, Mapping[str, str]],
    application_id: str,
    process_type: Literal["none", "fill", "no_fill"],
    study_programme_type: str,
) -> tuple[str | None, NotesDict]:
    session = flask.json.loads(application.application)
    notes = NotesDict()

    study_programmes: list[str] = []
    for prog in session["study_programme"]:
        if prog == "_":
            continue
        if STUDY_PROGRAMME_TYPES[prog] != study_programme_type:
            continue
        study_programmes.append(prog)

    if not study_programmes:
        raise NoValidProgramme()

    if await check_application_exists(ctx, application_id, study_programme_type):
        return None, NotesDict(application_exists=True)

    app, ops = await Application[EvidenciaUchadzacovPrihlasokDialogsType].open(
        ctx, VSPK014
    )

    # Ocakavame, ze sa otvoria dve okna
    op1, op2 = ops.expect_two(OpenDialogOp, OpenDialogOp)
    await op1.perform()
    await op2.perform()

    # Vyberieme prvy akademicky rok (ocakavane nasledujuci)
    await app.d.akademickyRokComboBox.select(0)
    await app.d.potvrditRokButton.click()

    # Zavrieme filter
    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()

    # Vyrobime novu prihlasku
    ops = await app.d.novyButton.click(return_ops=True)
    await ops.expect_one(OpenDialogOp).perform()

    # Opyta sa nas to na stupen studia
    selected_stupen = None
    for idx, option in enumerate(app.d.stupenComboBox.options):
        if option.id == PRIHLASKA_DEGREE[study_programme_type]:
            selected_stupen = idx
            break

    if selected_stupen is None:
        await app.force_close()
        raise Exception(
            f"Expected option {PRIHLASKA_DEGREE[study_programme_type]} in VSPK064 dialog, but not found."
        )

    await app.d.stupenComboBox.select(selected_stupen)

    ops = await app.d.enterButton.click(return_ops=True)

    # Ocakavame, ze sa zavrie tento dialog a otvori sa novy
    op1, op2 = ops.expect_two(CloseDialogOp, OpenDialogOp)
    await op1.perform()
    await op2.perform()

    ##########
    # Vyplname prihlasku
    ##########

    # Vymazeme obcianstvo
    await app.d.button16.click()

    await app.d.kodStatTextField.write(session["nationality"])

    await app.d.button3.click()

    # If the birth number is not filled in, just skip the whole "guess the
    # person by their birth number" part
    if len(session["birth_no"].strip()) != 0:
        await app.d.rodneCisloTextField.write(session["birth_no"])

        # Click on relevant rodneCisloButton
        ops = await app.d.rodneCisloButton.click(return_ops=True)

        # FIXME: This i here is simply one nasty hack. Its purpose is simple:
        # we really do not know what sort of an op will AIS return. Thus, we'll
        # try openDialog and confirmBox and throw an exception otherwise
        while len(ops) != 0:
            # Close the dialog if some shows up
            if ops.has_types(OpenDialogOp):
                await ops.expect_one(OpenDialogOp).perform()

                ops = await app.d.closeButton.click(return_ops=True)
                await ops.expect_one(CloseDialogOp).perform()

                break

            # It may happen that a confirmBox gets shown (for whatever reason).
            # Should that happen, the confirmBox should be just closed.
            elif ops.has_types(ConfirmBoxOp):
                ops = await ops.expect_one(ConfirmBoxOp).reply(
                    ConfirmBoxOp.Option.CANCEL, return_ops=True
                )

            else:
                await app.force_close()
                ops.expect_types(OpenDialogOp)  # Raise an exception

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
        await app.force_close()
        return None, notes

    # Turn off automatic generation of ID numbers for applications.
    await app.d.ecAutomatickyCheckBox.set_to(False)
    if study_programme_type == STUDY_PROGRAMME_BACHELORS:
        await app.d.evidCisloNumberControl.write(str(application.id))
    else:
        await app.d.evidCisloNumberControl.write(
            str(application.id + MASTERS_ID_OFFSET)
        )

    # If we are in the 'no_fill' process_type, the personal data and address
    # should be taken from whatever AIS2 provides
    if process_type != "no_fill":
        await app.d.menoTextField.write(session["basic_personal_data"]["name"])
        await app.d.priezviskoTextField.write(session["basic_personal_data"]["surname"])
        if (
            session["basic_personal_data"]["surname"]
            != session["basic_personal_data"]["born_with_surname"]
        ):
            await app.d.povPriezviskoTextField.write(
                session["basic_personal_data"]["born_with_surname"]
            )

        # This should basically never happen in production, but when testing,
        # it would be nice not to fail in case the application does not have
        # the submitted_at date filled in yet.
        if application.submitted_at is not None:
            await app.d.datumOdoslaniaDateControl.write(
                application.submitted_at.strftime("%d.%m.%Y")
            )
        await app.d.datumNarodeniaDateControl.write(session["date_of_birth"])

        # Sex selection
        if session["sex"] == "male":
            await app.d.kodPohlavieRadioBox.select(0)
        else:
            await app.d.kodPohlavieRadioBox.select(1)

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
        await app.d.c30Button.click()
        await app.d.c31Button.click()

        if session["country_of_birth"] == "703":
            place_of_birth_psc = lists["city_psc"][session["place_of_birth"]]
            await select_city_by_psc_ciselnik_code(
                app,
                place_of_birth_psc,
                session["place_of_birth"],
                app.d.sklonovanieNarTextField,
                app.d.vyberMiestoNarodeniabutton,
            )
        else:
            await app.d.statNarodeniaTextField.write(
                lists["country"][session["country_of_birth"]]
            )  # noqa
            await app.d.button22.click()

            await app.d.sklonovanieNarTextField.write(session["place_of_birth_foreign"])  # noqa

        await app.d.telefonTextField.write(session["phone"])
        await app.d.emailPrivateTextField.write(session["email"])

        # Address
        await fill_in_address("address_form", app, session, lists)

        # Correspondence address
        if session["has_correspondence_address"]:
            await app.d.pouzitPSAdresuCheckBox.toggle()
            await fill_in_address("correspondence_address", app, session, lists)

    programme_controls = [
        (app.d.program1TextField, app.d.button12, app.d.c11Button),
        (app.d.program2TextField, app.d.button13, app.d.c12Button),
        (app.d.program3TextField, app.d.button14, app.d.c13Button),
    ]

    for i, prog in enumerate(study_programmes):
        field, expand, confirm = programme_controls[i]

        # Vyplnime odbor
        await field.write(prog)

        # Nechame doplnit cely nazov odboru
        ops = await expand.click(return_ops=True)

        print("After filling in study programme: {}".format(ops), file=sys.stderr)

        # Deal with the dialog that opens up when a prefix of a programme
        # matches various options, e.g. FYZ and FYZ/k
        await choose_study_programme(app, ops, prog)

        # Nechame doplit povinne predmety
        await confirm.click()

    await app.d.rokZaverSkuskyNumberControl.write(
        str(session["basic_personal_data"]["matura_year"])
    )

    if session["finished_highschool_check"] == "SK":
        # 'XXXXXXX' signifies "highschool not found"
        if session["studies_in_sr"]["highschool"] != "XXXXXXX":
            await app.d.sSKodTextField.write(session["studies_in_sr"]["highschool"])
            await app.d.button10.click()

        await app.d.odborySkolyCheckBox.toggle()

        # 'XXXXXX' signifies 'study programme not found'
        if session["studies_in_sr"]["study_programme_code"] != "XXXXXX":
            await app.d.kodOdborTextField.write(
                session["studies_in_sr"]["study_programme_code"]
            )
            await app.d.c1Button.click()

        # Select correct option index based on education_level
        typ_vzdelania_index = None
        for idx, option in enumerate(app.d.sSKodTypVzdelaniaComboBox.options):
            if option.id == session["studies_in_sr"]["education_level"]:
                typ_vzdelania_index = idx

        if typ_vzdelania_index is not None:
            await app.d.sSKodTypVzdelaniaComboBox.select(typ_vzdelania_index)

    else:
        # foreign high school
        await app.d.sSKodTextField.write("999999999")
        await app.d.button10.click()

        # študijný odbor na zahraničnej škole
        await app.d.kodOdborTextField.write("0000500")

    # Remove all rows in vysvedceniaTable

    print("Final: {}".format(ops), file=sys.stderr)
    while len(await app.d.vysvedceniaTable.all_rows()) > 0:
        ops = await app.d.odobratButton.click(return_ops=True)
        print("Removing: {}".format(ops), file=sys.stderr)
        # really confirm
        ops = await ops.expect_one(ConfirmBoxOp).reply(
            ConfirmBoxOp.Option.YES, return_ops=True
        )

        # ConfirmBoxOp.reply() should return either [OpenDialogOp] or []
        if ops:
            await ops.expect_one(OpenDialogOp).perform()

            ops = await app.d.closeButton.click(return_ops=True)

            # closeButton.click() should return either [CloseDialogOp] or
            # [CloseDialogOp, OpenDialogOp]
            if len(ops) == 2:
                op1, op2 = ops.expect_two(CloseDialogOp, OpenDialogOp)
                await op1.perform()
                await op2.perform()

                # There should be only one CloseDialogOp this time
                ops = await app.d.closeButton.click(return_ops=True)

            await ops.expect_one(CloseDialogOp).perform()

    ABBRs, F = generate_subject_abbrevs(session)

    for abbr in ABBRs:
        await add_subject(app, abbr)
        await fill_in_table_cells(app, abbr, F, session)

    # Unselect everything in prilohyTable (literally)
    await unselect_table(app.d.prilohyTable)
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
        "LIST_PD_MAT": "ListPD",
        "LIST_PD_FYZ": "ListPD",
        "LIST_PD_INF": "ListPD",
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
    for idx, row in enumerate(await app.d.prilohyTable.all_rows()):
        if row.cells[1].value in checkboxes:
            await app.d.prilohyTable.edit_cell("checkBox", idx, True)

    # Prepare poznamka_text
    poznamka_items: list[str] = []
    if "SCIO" in checkboxes:
        poznamka_items.append("SCIO")
    if "ExtMat" in checkboxes:
        poznamka_items.append("ExternaMaturitaMat")

    poznamka_items.append(" ".join(session["study_programme"]))
    poznamka_items.append(f"EP#{application_id}{study_programme_type}")
    poznamka_text = "\n".join(poznamka_items)

    await app.d.poznamkaTextArea.write(poznamka_text)

    # Submit the app
    ops = await app.d.enterButton.click(return_ops=True)

    print("Post submit: {}".format(ops), file=sys.stderr)

    message_box_counter = 0

    while True:
        # ops should be [ConfirmBoxOp] or [MessageBoxOp] or [CloseDialogOp]

        if ops.has_types(ConfirmBoxOp):
            if "evidenčným číslom" in ops.expect_one(ConfirmBoxOp).message:
                # Generate new id number for the app
                await ops.expect_one(ConfirmBoxOp).reply(ConfirmBoxOp.Option.CANCEL)

                num = app.d.evidCisloNumberControl.bdvalue
                notes["app_id_exists"] = num

                await app.d.evidCisloNumberControl.write("")
                await app.d.ecAutomatickyCheckBox.toggle()

                # Click enterButton and try again
                ops = await app.d.enterButton.click(return_ops=True)

            else:
                # A set of confirm boxes may show up if highschool grades were filled in
                ops = await ops.expect_one(ConfirmBoxOp).reply(
                    ConfirmBoxOp.Option.YES, return_ops=True
                )

            print("After confirm box: {}".format(ops), file=sys.stderr)

        elif ops.has_types(MessageBoxOp) and message_box_counter == 0:
            message_box_counter += 1

            if "existuje osoba s Vami zadaným emailom." in app.d.statusHtmlArea.content:
                email = app.d.emailPrivateTextField.value
                notes["email_exists"] = email
                await app.d.emailPrivateTextField.write("")

            # Click enterButton and try again
            ops = await app.d.enterButton.click(return_ops=True)

            print("After message box: {}".format(ops), file=sys.stderr)

        else:
            errors = app.d.statusHtmlArea.content
            await ops.expect_one(CloseDialogOp).perform()
            break

    print("errors: {}".format(errors), file=sys.stderr)

    await app.force_close()
    return errors, notes


async def fill_in_address(
    field: Literal["address_form", "correspondence_address"],
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType],
    session: SessionDict,
    lists: Mapping[str, Mapping[str, str]],
) -> None:
    if field == "address_form":
        city_field = app.d.trIdObecTextField
        city_button = app.d.button4
        posta_field = app.d.trPostaTextField
        country_button = app.d.button5
        country_field = app.d.trKodStatTextField
        street = app.d.trUlicaTextField
        street_no = app.d.trOrientacneCisloTextField
        postal_no = app.d.trPSCTextField
    else:
        city_field = app.d.psIdObecTextField
        city_button = app.d.button7
        posta_field = app.d.psPostaTextField
        country_button = app.d.button8
        country_field = app.d.psKodStatTextField
        street = app.d.psUlicaTextField
        street_no = app.d.psOrientacneCisloTextField
        postal_no = app.d.psPSCTextField

    if session[field]["country"] == "703":
        # Local (SR) address
        city = lists["city"][session[field]["city"]]
        city = re.sub(r",[^,]+$", "", city)
        city_psc = lists["city_psc"][session[field]["city"]]

        # First write country to the country field (even in case of SK)
        await country_field.write(lists["country"][session[field]["country"]])
        await country_button.click()

        await select_city_by_psc_ciselnik_code(
            app, city_psc, session[field]["city"], city_field, city_button
        )

        # TODO: hack to work with current AIS
        # Write the actual city to "Post office" field
        await posta_field.write(city)
    else:
        # Foreign (non SR) address
        await country_field.write(lists["country"][session[field]["country"]])

        await country_button.click()

        await posta_field.write(session[field]["city_foreign"])

    await street.write(session[field]["street"])
    await street_no.write(session[field]["street_no"])

    await postal_no.write(session[field]["postal_no"][:10])


def add_to_set_on_grade_field(
    S: set[str], F: set[str], session: SessionDict, grade_field: str, abbr: str
) -> None:
    if grade_field in session and "grade_first_year" in session[grade_field]:
        S.add(abbr)
        F.add(grade_field)


def add_to_set_on_further_study_info(
    S: set[str], F: set[str], session: SessionDict, field: str, abbr: str
) -> None:
    if (
        "further_study_info" in session
        and field in session["further_study_info"]
        and session["further_study_info"][field]
    ):
        S.add(abbr)
        F.add(field)


def generate_subject_abbrevs(session: SessionDict) -> tuple[set[str], set[str]]:
    ABBRs = set[str]()
    F = set[str]()
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


def generate_checkbox_abbrs(session: SessionDict) -> set[str]:
    checkboxes = set[str]()
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


def add_further_study_info_checkbox(
    checkboxes: set[str], session: SessionDict, field: str, chkb: str
) -> None:
    if (
        "further_study_info" in session
        and field in session["further_study_info"]
        and session["further_study_info"][field]
    ):
        checkboxes.add(chkb)


async def add_subject(
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType], abbr: str
) -> None:
    # Add new rows (subjects)
    ops = await app.d.novyButton.click(return_ops=True)
    await ops.expect_one(OpenDialogOp).perform()

    rows = await app.d.table.all_rows()
    row_index = None
    for idx, row in enumerate(rows):
        if row.cells[4].value == abbr:
            row_index = idx

    if row_index is not None:
        await app.d.table.select(row_index)
    else:
        raise Exception("Could not find {}".format(abbr))

    # Submit the dialog
    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()

    # Add 'N' to subject level, if such a cell exists
    index = len(await app.d.vysvedceniaTable.all_rows()) - 1
    if "kodUrovenMat" in app.d.vysvedceniaTable.column_map:
        await app.d.vysvedceniaTable.edit_cell("kodUrovenMat", index, "N")


async def fill_in_table_cells(
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType],
    abbr: str,
    F: set[str],
    session: SessionDict,
) -> None:
    if abbr == "M":
        if "external_matura_percentile" in F:
            p = session["further_study_info"]["external_matura_percentile"]
            index = len(await app.d.vysvedceniaTable.all_rows()) - 1
            await app.d.vysvedceniaTable.edit_cell("percentil", index, p)

        if "matura_mat_grade" in F:
            await matura_grade_to_table_cell(app, session, "matura_mat_grade")

        if "grades_mat" in F:
            await grades_to_table_cells(app, session, "grades_mat")

    if abbr == "F":
        if "matura_fyz_grade" in F:
            await matura_grade_to_table_cell(app, session, "matura_fyz_grade")

        if "grades_fyz" in F:
            await grades_to_table_cells(app, session, "grades_fyz")

    if abbr == "B":
        if "matura_bio_grade" in F:
            await matura_grade_to_table_cell(app, session, "matura_bio_grade")

        if "grades_bio" in F:
            await grades_to_table_cells(app, session, "grades_bio")

    if abbr == "CH":
        if "matura_che_grade" in F:
            await matura_grade_to_table_cell(app, session, "matura_che_grade")

        if "grades_che" in F:
            await grades_to_table_cells(app, session, "grades_che")

    if abbr == "I":
        if "matura_inf_grade" in F:
            await matura_grade_to_table_cell(app, session, "matura_inf_grade")

        if "grades_inf" in F:
            await grades_to_table_cells(app, session, "grades_inf")

    if abbr == "IP":
        if "scio_percentile" in F or "scio_date" in F:
            p = session["further_study_info"]["scio_percentile"]
            d = session["further_study_info"]["scio_date"]
            desc = "SCIO {}".format(d)
            index = len(await app.d.vysvedceniaTable.all_rows()) - 1
            await app.d.vysvedceniaTable.edit_cell("popis", index, desc)
            await app.d.vysvedceniaTable.edit_cell("percentil", index, p)


async def grades_to_table_cells(
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType],
    session: SessionDict,
    grades_field: str,
) -> None:
    first = session[grades_field]["grade_first_year"]
    second = session[grades_field]["grade_second_year"]
    third = session[grades_field]["grade_third_year"]
    index = len(await app.d.vysvedceniaTable.all_rows()) - 1

    if first:
        await app.d.vysvedceniaTable.edit_cell("znamkaI", index, first)
    if second:
        await app.d.vysvedceniaTable.edit_cell("znamkaII", index, second)
    if third:
        await app.d.vysvedceniaTable.edit_cell("znamkaIII", index, third)


async def matura_grade_to_table_cell(
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType],
    session: SessionDict,
    grade_field: str,
) -> None:
    g = session["further_study_info"][grade_field]
    index = len(await app.d.vysvedceniaTable.all_rows()) - 1
    await app.d.vysvedceniaTable.edit_cell("znamkaMaturitna", index, g)


async def unselect_table(table: Table) -> None:
    """
    Unselect all first checkboxes in a table. Don't ask me why.
    """
    for idx, _row in enumerate(await table.all_rows()):
        await table.edit_cell("checkBox", idx, False)


async def choose_study_programme(
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType],
    ops: Operations,
    study_programme: str,
) -> None:
    # Do nothing if there is no dialog to be opened
    if len(ops) == 0:
        return

    await ops.expect_one(OpenDialogOp).perform()

    rows = await app.d.table.all_rows()
    row_index = None
    for idx, row in enumerate(rows):
        if row.cells[0].value == study_programme:
            row_index = idx

    # If we did find a row, let's select it
    if row_index is not None:
        await app.d.table.select(row_index)
    else:
        raise Exception("Could not find {}".format(study_programme))

    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()


async def select_city_by_psc_ciselnik_code(
    app: Application[EvidenciaUchadzacovPrihlasokDialogsType],
    city_psc: str,
    ciselnik_code: str,
    city_field: TextField,
    city_button: Button,
) -> None:
    # Write PSC instead of city name (TODO: hack to work with current AIS)
    await city_field.write(city_psc)
    ops = await city_button.click(return_ops=True)

    if len(ops) == 0:
        return

    # Open selection dialogue
    await ops.expect_one(OpenDialogOp).perform()

    rows = await app.d.table.all_rows()

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
        await app.d.table.select(row_index)
    else:
        raise Exception("Could not find ciselnik_code {}".format(city_psc))

    # Close selection dialogue
    ops = await app.d.enterButton.click(return_ops=True)
    await ops.expect_one(CloseDialogOp).perform()
