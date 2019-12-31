from flask_babel import gettext as _
from flask_uploads import UploadSet
from .utils import choices_from_csv, city_formatter, okres_fixer
import os
import enum

DIR = os.path.dirname(os.path.abspath(__file__))

SELECT_STUDY_PROGRAMME = _('Vyberte si, prosím, aspoň prvý študijný program')
NO_ACCESS_MSG = _('Nemáte oprávnenie pre prístup k danému prístupovému bodu')
DEAN_LIST_MSG = _('Na základe listu dekana nie je potrebné zadávať údaje o prospechu na strednej škole.')  # noqa
LOGIN_CONGRATS_MSG = _('Gratulujeme, boli ste prihlásení do prostredia ePrihlaska!')  # noqa
PASSWD_CHANGED_MSG = _('Gratulujeme, Vaše heslo bolo nastavené! Prihláste sa ním, prosím, nižšie.')  # noqa
INVALID_TOKEN_MSG = _('Váš token na zmenu hesla je neplatný. Vyplnte prosím Váš email znovu.')  # noqa

SUBMISSIONS_NOT_OPEN = _('Podávanie prihlášok momentálne nie je otvorené.')

FLASH_MSG_DATA_SAVED = _('Vaše dáta boli uložené!')
FLASH_MSG_DATA_NOT_SAVED = _('Vaše dáta neboli uložené, vyplnený formulár obsahuje chybu! Opravte vyznačené chyby a uložte dáta znovu.')
FLASH_MSG_FILL_FORM = _('Najprv, prosím, vyplňte formulár uvedený nižšie')
FLASH_MSG_APP_SUBMITTED = _('Gratulujeme, Vaša prihláška bola podaná!')
FLASH_MSG_WRONG_LOGIN = _('Nesprávne prihlasovacie údaje.')
FLASH_MSG_AFTER_LOGIN = _('Gratulujeme, boli ste prihlásení do prostredia '
                          'ePrihlaska!')
FLASH_MSG_RECEIPT_SUBMITTED = _('Priložený súbor s potvrdením o zaplatení bol '
                                'uložený.')

SUBMIT = _('Odoslať')
NEXT = _('Ulož a pokračuj')
CONTINUE = _('Pokračovať')
SUBMIT_APPLICATION = _('Podať prihlášku')

NATIONALITY = _('Štátne občianstvo')
NAME = _('Meno')
SURNAME = _('Priezvisko')
BORNWITH_SURNAME = _('Rodné priezvisko')

MARITAL_STATUS = _('Rodinný stav')
SEX = _('Pohlavie')

MALE = _('muž')
FEMALE = _('žena')

BIRTH_NO = _('Rodné číslo')
BIRTH_DATE = _('Dátum narodenia')
BIRTH_COUNTRY = _('Štát narodenia')
BIRTH_PLACE = _('Miesto narodenia')
BIRTH_PLACE_FOREIGN = _('Miesto narodenia (v&nbsp;zahraničí)')

EMAIL = _('Email')
PHONE_CONTACT = _('Telefónny kontakt')

BASIC_PERSONAL_DATA = _('Základné údaje')

FURTHER_PERSONAL_DATA = _('Ďalšie osobné údaje')
INFO_FATHER = _('Informácie o otcovi')
INFO_MATHER = _('Informácie o matke')


FATHER_NAME = _('Meno otca')
FATHER_SURNAME = _('Priezvisko otca')
FATHER_BORNWITH_SURNAME = _('Rodné priezvisko otca')

MOTHER_NAME = _('Meno matky')
MOTHER_SURNAME = _('Priezvisko matky')
MOTHER_BORNWITH_SURNAME = _('Rodné priezvisko matky')

PERSONAL_INFO_CHECK = _('Dávam súhlas, aby vysoká škola spracúvala moje osobné údaje obsiahnuté v tejto prihláške a jej prílohách na účely prijímacieho konania až do termínu konania zápisu do 1. ročníka štúdia na vysokej škole.')  # noqa

DEAN_INV_LIST_YN = _('Dostal(a) som list od dekana')
DEAN_INV_LIST_NO = _('Číslo listu od dekana')
DEAN_INV_LIST_NO_DESC = _('Prosím, vyplňte číslo listu od dekana, ktorý ste dostali')  # noqa

PRG_MAT = _('Matematika')
PRG_PMA = _('Poistná matematika')
PRG_EFM = _('Ekonomická a finančná matematika')
PRG_MMN = _('Manažérska matematika')
PRG_FYZ = _('Fyzika')
PRG_BMF = _('Biomedicínska fyzika')
PRG_OZE = _('Obnoviteľné zdroje energie a environmentálna fyzika')
PRG_TEF = _('Technická fyzika')
PRG_INF = _('Informatika')
PRG_AIN = _('Aplikovaná informatika')
PRG_BIN = _('Bioinformatika')
PRG_DAV = _('Dátová veda')
PRG_upMAFY = _('Učiteľstvo matematiky a fyziky')
PRG_upMAIN = _('Učiteľstvo matematiky a informatiky')
PRG_upFYIN = _('Učiteľstvo fyziky a informatiky')
PRG_upMATV = _('Učiteľstvo matematiky a telesnej výchovy')
PRG_upMADG = _('Učiteľstvo matematiky a deskriptívnej geometrie')
PRG_upINBI = _('Učiteľstvo informatiky a biológie')
PRG_upINAN = _('Učiteľstvo informatiky a anglického jazyka a literatúry')

MATURA_YEAR = _('Rok maturity')

STUDY_PROGRAMMES = _('Študijné programy')
STUDY_PROGRAMME_1 = _('Prvý študijný program')
STUDY_PROGRAMME_2 = _('Druhý študijný program')
STUDY_PROGRAMME_3 = _('Tretí študijný program')
STUDY_PROGRAMME_DESC = _('Vyberte si aspoň jeden a najviac tri študijné programy. Poradie študijných programov vyjadruje preferenciu uchádzača a je záväzné, napr. v prípade splnenia podmienok na dva študijné programy bude uchádzač prijatý na ten, ktorý bude uvedený na prvom mieste.')  # noqa
STUDY_PROGRAMME_CHOICES = [('_', _('žiaden')),
                           ('MAT', PRG_MAT),
                           ('PMA', PRG_PMA),
                           ('EFM', PRG_EFM),
                           ('MMN', PRG_MMN),
                           ('FYZ', PRG_FYZ),
                           ('BMF', PRG_BMF),
                           ('OZE', PRG_OZE),
                           ('TEF', PRG_TEF),
                           ('INF', PRG_INF),
                           ('AIN', PRG_AIN),
                           ('BIN', PRG_BIN),
                           ('DAV', PRG_DAV),
                           ('upMAFY', PRG_upMAFY),
                           ('upMAIN', PRG_upMAIN),
                           ('upFYIN', PRG_upFYIN),
                           ('upMATV', PRG_upMATV),
                           ('upMADG', PRG_upMADG),
                           ('upINBI', PRG_upINBI),
                           ('upINAN', PRG_upINAN)]

# STUDY_PROGRAMME_CHOICES_ACTIVE = STUDY_PROGRAMME_CHOICES
STUDY_PROGRAMME_CHOICES_ACTIVE = [('_', _('žiaden')),
                           ('MAT', PRG_MAT),
                           ('PMA', PRG_PMA),
                           ('MMN', PRG_MMN),
                           ('FYZ', PRG_FYZ),
                           ('OZE', PRG_OZE),
                           ('TEF', PRG_TEF),
                           ('AIN', PRG_AIN),
                           ('upMAFY', PRG_upMAFY),
                           ('upMAIN', PRG_upMAIN),
                           ('upFYIN', PRG_upFYIN),
                           ('upMADG', PRG_upMADG),
                           ('upINBI', PRG_upINBI),
                           ('upINAN', PRG_upINAN)]

ADDRESS_COUNTRY = _('Štát')
ADDRESS_STREET = _('Ulica')
ADDRESS_NO = _('Číslo')
ADDRESS_CITY = _('Mesto (obec)')
ADDRESS_CITY_FOREIGN = _('Mesto (v zahraničí)')
ADDRESS_POSTAL_NO = _('PSČ')
ADDRESS_CITY_FOREIGN_FILL = _('Napíšte, prosím, názov mesta.')

ADDRESS_STREET_DESC = _('V prípade, že sa jedná o malú obec bez názvov ulíc, napíšte názov obce.')  # noqa

PERMANENT_ADDRESS = _('Adresa trvalého bydliska')
HAS_CORRESPONDENCE_ADDRESS = _('Korešpondenčná adresa sa nezhoduje s adresou trvalého bydliska')  # noqa
CORRESPONDENCE_ADDRESS = _('Korešpondenčná adresa')

HAS_PREVIOUSLY_STUDIED = _('V minulosti som študoval(a) na vysokej škole v SR v I. stupni štúdia alebo v spojenom I. a II. stupni štúdia (úspešne alebo neúspešne)')  # noqa
FINISHED_HIGHSCHOOL = _('Absolvovaná stredná škola')
IN_SR = _('v Slovenskej republike')
OUTSIDE_OF_SR = _('mimo Slovenskej republiky')

HIGHSCHOOL = _('Navštevovaná stredná škola')
HIGHSCHOOL_DESC = _('V prípade, že vaša stredná škola nie je v zozname, zvoľte možnosť "Moja stredná škola nie je v zozname" (na začiatku zoznamu)')  # noqa
STUDY_PROGRAMME_CODE = _('Kód študijného odboru')
STUDY_PROGRAMME_CODE_DESC = _('Kód študijného odboru je uvedený na vašom vysvedčení. V prípade, že na vysvedčení nemáte uvedený jeden z týchto študijných kódov, zvoľte "nemám kód študijného odboru" (na začiatku zoznamu)')  # noqa
HS_EDUCATION_LEVEL = _('Dosiahnuté / očakávané stredoškolské vzdelanie')
FOREIGN_FINISHED_HIGHSCHOOL = _('Absolvoval(a) som / absolvujem strednú školu s maturitou mimo SR')  # noqa

FOREIGN_STUDIES = _('Štúdium mimo SR')
STUDIES_IN_SR = _('Štúdium na Slovensku')

COMPETITION_CHOICES = [
    ('_', _('neuvádzam výsledok zo súťaže')),
    ('MAT', _('úspešný riešiteľ - Matematická olympiáda A alebo B - krajské alebo celoštátne kolo')),  # noqa
    ('FYZ', _('úspešný riešiteľ - Fyzikálna olympiáda A alebo B - krajské alebo celoštátne kolo')),  # noqa
    ('INF', _('úspešný riešiteľ - Olympiáda v informatike A alebo B - krajské alebo celoštátne kolo')),  # noqa
    ('BIO', _('úspešný riešiteľ - Biologická olympiáda A alebo B - krajské alebo celoštátne kolo')),  # noqa
    ('CHM', _('úspešný riešiteľ - Chemická olympiáda A alebo B - krajské alebo celoštátne kolo')),  # noqa
    ('SOC_MAT', _('úspešný účastník - Stredoškolská odborná činnost odbor 02 matematika, fyzika - celoštátne kolo')),  # noqa
    ('SOC_INF', _('úspešný účastník - Stredoškolská odborná činnosť odbor 11 informatika - celoštátne kolo')),  # noqa
    ('SOC_BIO', _('úspešný účastník - Stredoškolská odborná činnosť odbor 04 biológia - celoštátne kolo')),  # noqa
    ('SOC_CHM', _('úspešný účastník - Stredoškolská odborná činnosť odbor 03 chémia, potravinárstvo - celoštátne kolo')),  # noqa
    ('TMF', _('úspešný riešiteľ - Turnaj mladých fyzikov - celoštátne kolo')),
    ('FVAT_MAT', _('úspešný účastník - Festival vedy a techniky kategória Matematika - celoštátne kolo')),
    ('FVAT_FYZ', _('úspešný účastník - Festival vedy a techniky kategória Fyzika a astronómia - celoštátne kolo')),
    ('FVAT_INF', _('úspešný účastník - Festival vedy a techniky kategória Informatika a počítačové inžinierstvo - celoštátne kolo')),
    ('FVAT_BIO', _('úspešný účastník - Festival vedy a techniky kategória Biológia - celoštátne kolo')),
    ('FVAT_MAT', _('úspešný účastník - Festival vedy a techniky kategória Chémia - celoštátne kolo')),
    ('ROBOCUP', _('postup do medzinárodného kola - RoboCupJunior')),
    ('IBOBOR', _('percentil aspoň 90 - iBobor - kategória Senior')),
    ('ZENIT', _('úspešný riešiteľ - Súťaž ZENIT v programovaní - krajské kolo')),
    ('TROJSTEN_KMS', _('65% bodov v ľubovoľnej kategórii - KMS (TROJSTEN) - ktorýkoľvek ročník a časť')),
    ('TROJSTEN_FKS', _('65% bodov v ľubovoľnej kategórii - FKS (TROJSTEN) - ktorýkoľvek ročník a časť')),
    ('TROJSTEN_KSP', _('65% bodov v ľubovoľnej kategórii - KSP (TROJSTEN) - ktorýkoľvek ročník a časť')),    
]

COMPETITION_YEAR = _('Rok')
COMPETITION_NAME = _('Názov súťaže')
COMPETITION_FURTHER_INFO = _('Ďalšie informácie')
COMPETITION_FURTHER_INFO_DESC = _('V prípade krajského kola do tohto poľa prosím napíšte názov kraja, v ktorom sa daná súťaž konala. V prípade iných kôl do tohto poľa prosím vpíšte akékoľvek iné informácie, ktoré by mohli pomôcť pri identifikácii vášho úspechu.')  # noqa

COMPETITION_FIRST = _('Úspech na súťaži (1)')
COMPETITION_SECOND = _('Úspech na súťaži (2)')
COMPETITION_THIRD = _('Úspech na súťaži (3)')

EXTERNAL_MATURA_PERCENTILE = _('percentil externej maturity z matematiky '
                               '(SR) / maturitního didaktického testu z '
                               'matematiky (ČR)')

SCIO_PERCENTILE = _('percentil autorizovanej skúšky z matematiky (SCIO)')
SCIO_DATE = _('dátum vykonania autorizovanej skúšky z matematiky (SCIO)')
SCIO_CERT_NO = _('číslo certifikátu SCIO')
SCIO_CERT_NO_DESC = _('V prípade, že ste autorizovanú skúšku z matematiky (SCIO) už v minulosti absolvovali, do tohto poľa prosím napíšte číslo certifikátu, ktorý ste po jej vykonaní obdržali. Zrýchlite tak proces spracovania Vašej prihlášky. Ďakujeme!') # noqa

MATURA_MAT_GRADE = _('známka z maturity z matematiky')
MATURA_FYZ_GRADE = _('známka z maturity z fyziky')
MATURA_INF_GRADE = _('známka z maturity z informatiky')
MATURA_CHE_GRADE = _('známka z maturity z chémie')
MATURA_BIO_GRADE = _('známka z maturity z biológie')

WILL_TAKE_EXT_MAT = _('zúčastním sa externej maturity z matematiky (SR) /'
                      ' maturitního didaktického testu z matematiky (ČR)')
WILL_TAKE_SCIO = _('zúčastním sa autorizovanej skúšky z matematiky (SCIO)')  # noqa
WILL_TAKE_MAT_MATURA = _('maturujem z matematiky')
WILL_TAKE_FYZ_MATURA = _('maturujem z fyziky')
WILL_TAKE_INF_MATURA = _('maturujem z informatiky')
WILL_TAKE_BIO_MATURA = _('maturujem z biológie')
WILL_TAKE_CHE_MATURA = _('maturujem z chémie')

FURTHER_STUDY_INFO = _('Autorizovaná skúška z matematiky a maturity')

GRADE_FIRST_YEAR = {
    '4': _('koncoročná známka v 1. ročníku'),
    '8': _('koncoročná známka v kvinte'),
    '5': _('koncoročná známka v 2. ročníku'),
    '0': _('koncoročná známka v ročníku n-3, kde n je počet ročníkov')
}
GRADE_SECOND_YEAR = {
    '4': _('koncoročná známka v 2. ročníku'),
    '8': _('koncoročná známka v sexte'),
    '5': _('koncoročná známka v 3. ročníku'),
    '0': _('koncoročná známka v ročníku n-2, kde n je počet ročníkov')
}
GRADE_THIRD_YEAR = {
    '4': _('koncoročná známka v 3. ročníku'),
    '8': _('koncoročná známka v septime'),
    '5': _('koncoročná známka v 4. ročníku'),
    '0': _('koncoročná známka v ročníku n-1, kde n je počet ročníkov')
}

GRADES_MAT = _('Známky z matematiky')
GRADES_INF = _('Známky z informatiky')
GRADES_FYZ = _('Známky z fyziky')
GRADES_BIO = _('Známky z biológie')
GRADES_CHE = _('Známky z chémie')

GRADE_ERR = _('Zle zadaná známka. Akceptované známky sú 1 až 5.')

FINAL_NOTE = _('Poznámka')
FINAL_NOTE_SDESC = ('Ďalšie skutočnosti, ktoré chcete uviesť')
FINAL_NOTE_DESC = _('Prosím, informujte nás o skutočnostiach, ktoré by mohli byť pre Vašu prihlášku relevantné a neboli spomenuté v už vyplnených častiach.') # noqa

MENU = [
    (_('ePrihlaska'), 'index'),
    (_('Študijné programy'), 'study_programme'),
    (_('Osobné údaje'), 'personal_info'),
    (_('Adresa'), 'address'),
    (_('Predchádzajúce štúdium'), 'previous_studies'),
    (_('Výsledky a úspechy'), 'admissions_waivers'),
    (_('Záverečné pokyny'), 'final')
]

USERNAME = _('Používateľské meno')
PASSWORD = _('Heslo')
REPEAT_PASSWORD = _('Zopakujte heslo')
REPEAT_PASSWORD_ERR = _('Zadané heslá sa nezhodujú')
LOGIN = _('Prihlásiť')
SIGNUP = _('Zaregistrovať')
LOGOUT = _('Odhlásiť')
WELCOME = _('Vitajte {}')

FORGOTTEN_PASSWORD_MAIL = _('V rámci systému elektronickej prihlášky FMFI UK bol pre Váš účet aktivovaný postup pre zmenu zabudnutého hesla. Ak chcete heslo zmeniť, použite nasledujúci link: {}\n\nV inom prípade prosím tento email ignorujte.\n\nS pozdravom,\nhttps://prihlaska.fmph.uniba.sk')  # noqa

FORGOTTEN_PASSWORD_MSG = _('Ak bol poskytnutý e-mail nájdený, boli naň zaslané informácie o ďalšom postupe.')  # noqa

NEW_USER_MAIL = _('Vitajte v systéme elektronickej prihlášky FMFI UK. Pre vytvorenie hesla a následné prihlásenie prosím použite nasledujúci link: {}\n\nS pozdravom,\nhttps://prihlaska.fmph.uniba.sk')  # noqa

NEW_USER_MSG = _('Nový používateľ bol zaregistrovaný. Pre zadanie hesla prosím pokračujte podľa pokynov zaslaných na zadaný email.')  # noqa

YEAR_ERR = _('Nesprávne zadaná hodnota. Akceptované hodnoty sú v rozsahu od %(min)s po %(max)s')  # noqa

SEX_CHOICES = [('male', MALE),
               ('female', FEMALE)]
COUNTRY_CHOICES = choices_from_csv(DIR + '/data/staty.csv',
                                   ['id', 'Štát'],
                                   sortby=1,
                                   prepend=['703', '203'])

SELECT_CITY_CHOICE = [('999999', _('Zvoľte mesto alebo obec v SR'))]
CITY_CHOICES = choices_from_csv(DIR + '/data/obce.csv',
                                ['id', 'Názov obce', 'Okres'],
                                fmt='{1}, okr. {2}',
                                extend_with=SELECT_CITY_CHOICE,
                                sortby=1,
                                prepend=['999999'],
                                post_fmt=okres_fixer)

CITY_CHOICES_PSC = choices_from_csv(DIR + '/data/obce.csv',
                                    ['id', 'PSČ'],
                                    fmt='{1}')

MARITAL_STATUS_CHOICES = choices_from_csv(DIR + '/data/rodinne-stavy.csv',
                                          ['id', 'Rodinný stav'])

LENGTH_OF_STUDY = 'Dĺžka štúdia na strednej škole'
LENGTH_OF_STUDY_CHOICES = [('4', _('4 roky')),
                           ('5', _('5 rokov')),
                           ('8', _('8 rokov')),
                           ('0', _('iná'))]
LENGTH_OF_STUDY_DEFAULT = '4'


HIGHSCHOOL_NOT_IN_LIST = [('XXXXXXX',
                           _('Moja stredná škola nie je v zozname'))]
HIGHSCHOOL_CHOICES = choices_from_csv(DIR + '/data/skoly.csv',
                                      ['St. šk.', 'Obec', 'Stredná škola',
                                       'Ulica'],
                                      fmt='{1}, {2}, {3}',
                                      extend_with=HIGHSCHOOL_NOT_IN_LIST,
                                      sortby=1,
                                      prepend=['XXXXXXX'],
                                      post_fmt=city_formatter)

NO_SP_CHOICE = [('XXXXXX', _('nemám kód študijného odboru'))]
HS_STUDY_PROGRAMME_CHOICES = choices_from_csv(DIR + '/data/odbory.csv',
                                              ['Odbor - kod',
                                               'Odbor stred. školy'],
                                              extend_with=NO_SP_CHOICE,
                                              prepend=['XXXXXX'],
                                              fmt='{0} - {1}')

HS_STUDY_PROGRAMME_MAP = choices_from_csv(DIR + '/data/ss-odbor-map.csv',
                                          ['St. šk.', 'Odbor - kod'],
                                          fmt='{1}')

EDUCATION_LEVEL_CHOICES = choices_from_csv(DIR + '/data/vzdelanie.csv',
                                           ['Kód', 'Skrát. popis'],
                                           fmt='({0}) - {1}')

APPLICATION_STATES = [_('rozpracovaná'),
                      _('podaná'),
                      _('vytlačená'),
                      _('spracovaná')]


class ApplicationStates(enum.Enum):
    in_progress = 0
    submitted = 1
    printed = 2
    processed = 3


PAYMENT_RECEIPT = _('Potvrdenie o zaplatení')
ERR_EMPTY_FILE = _('Odovzdaný súbor bol prázdny.')
ERR_EXTENSION_NOT_ALLOWED = _('Povolené sú iba súbory PDF, JPG, BMP a PNG.')
ERR_RECEIPT_NOT_UPLOADED = _('Potvrdenie o zaplatení nebolo odoslané.')

receipts = UploadSet('receipts', ['pdf', 'jpg', 'bmp', 'png'])

# for the regular applications (before june) set to the same year
# for the additional application (after june) set CURRENT_MATURA_YEAR to next year
# this is soooo much fun!
CURRENT_MATURA_YEAR = 2020
DEFAULT_MATURA_YEAR = 2020
