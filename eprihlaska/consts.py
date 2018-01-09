from flask_babel import gettext as _
from .utils import choices_from_csv, city_formatter, okres_fixer
import os
import enum

DIR = os.path.dirname(os.path.abspath(__file__))

SUBMIT = _('Odoslať')
NEXT = _('Ďalej')

NATIONALITY = _('Občianstvo')
NAME = _('Meno')
SURNAME = _('Priezvisko')
BORNWITH_SURNAME = _('Rodné priezvisko')

MARITAL_STATUS = _('Rodinný stav')
SEX = _('Pohlavie')

MALE = _('muž')
FEMALE = _('žena')

BIRTH_NO = _('Rodné číslo')
BIRTH_DATE = _('Dátum narodenia')
BIRTH_COUNTRY = _('Krajina narodenia')
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

DEAN_INV_LIST_YN = _('Dostal som list od dekana')
DEAN_INV_LIST_NO = _('Číslo listu od dekana')
DEAN_INV_LIST_NO_DESC = _('Prosím, vyplňte číslo listu od dekana, ktorý ste dostali')

PRG_MAT = _('Matematika')
PRG_PMA = _('Poistná matematika')
PRG_EFM = _('Ekonomická a finančná matematika')
PRG_MNN = _('Manažérska matematika')
PRG_FYZ = _('Fyzika')
PRG_BMF = _('Biomedicínska fyzika')
PRG_OZE = _('Obnoviteľné zdroje energie a environmentálna fyzika')
PRG_INF = _('Informatika')
PRG_AIN = _('Aplikovaná informatika')
PRG_BIN = _('Bioinformatika')
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
STUDY_PROGRAMME_DESC = _('Vyberte si aspoň jeden a najviac tri študijné programy. Poradie študijných programov vyjadruje preferenciu uchádzača a je záväzné, napr. v prípade splnenia podmienok na dva študijné programy bude uchádzač prijatý na ten, ktorý bude uvedený na prvom mieste.')
STUDY_PROGRAMME_CHOICES = [('_', _('žiaden')),
                            ('MAT', PRG_MAT),
                            ('PMA', PRG_PMA),
                            ('EFM', PRG_EFM),
                            ('MMN', PRG_MNN),
                            ('FYZ', PRG_FYZ),
                            ('BMF', PRG_BMF),
                            ('OZE', PRG_OZE),
                            ('INF', PRG_INF),
                            ('AIN', PRG_AIN),
                            ('BIN', PRG_BIN),
                            ('upMAFY', PRG_upMAFY),
                            ('upMAIN', PRG_upMAIN),
                            ('upFYIN', PRG_upFYIN),
                            ('upMATV', PRG_upMATV),
                            ('upMADG', PRG_upMADG),
                            ('upINBI', PRG_upINBI),
                            ('upINAN', PRG_upINAN)]

ADDRESS_COUNTRY = _('Krajina')
ADDRESS_STREET = _('Ulica')
ADDRESS_NO = _('Číslo')
ADDRESS_CITY = _('Mesto')
ADDRESS_CITY_FOREIGN = _('Mesto (v zahraničí)')
ADDRESS_POSTAL_NO = _('PSČ')

PERMANENT_ADDRESS = _('Adresa trvalého bydliska')
HAS_CORRESPONDENCE_ADDRESS = _('Korešpondenčná adresa sa nezhoduje s adresou trvalého bydliska')
CORRESPONDENCE_ADDRESS = _('Korešpondenčná adresa')

HAS_PREVIOUSLY_STUDIED = _('V minulosti som študoval(a) na vysokej škole v SR v I. stupni štúdia alebo v spojenom I. a II. stupni štúdia (úspešne alebo neúspešne)')
FINISHED_HIGHSCHOOL = _('Absolvovaná stredná škola')
IN_SR = _('v Slovenskej republike')
OUTSIDE_OF_SR = _('mimo Slovenskej republiky')

HIGHSCHOOL = _('Navštevovaná stredná škola')
HIGHSCHOOL_DESC = _('V prípade, že vaša stredná škola nie je v zozname, zvoľte možnosť "Moja stredná škola nie je v zozname" (na začiatku zoznamu)')
STUDY_PROGRAMME_CODE = _('Kód študijného programu')
STUDY_PROGRAMME_CODE_DESC = _('Kód študijného programu je uvedený na vašom vysvedčení. V prípade, že na vysvedčení nemáte uvedený jeden z týchto študijných kódov, zvoľte "nemám kód študijného odboru" (na začiatku zoznamu)')
HS_EDUCATION_LEVEL = _('Dosiahnuté / očakávané stredoškolské vzdelanie')
FOREIGN_FINISHED_HIGHSCHOOL = _('Absolvoval(a) som / absolvujem strednú školu s maturitou mimo SR')

FOREIGN_STUDIES = _('Štúdium mimo SR')
STUDIES_IN_SR = _('Štúdium na Slovensku')

COMPETITION_CHOICES = [
    ('_', _('neuvádzam výsledok zo súťaže')),
    ('MAT', _('úspešný riešiteľ - Matematická olympiáda A alebo B - krajské alebo celoštátne kolo')),
    ('FYZ', _('úspešný riešiteľ - Fyzikálna olympiáda A alebo B - krajské alebo celoštátne kolo')),
    ('INF', _('úspešný riešiteľ - Olympiáda v informatike A alebo B - krajské alebo celoštátne kolo')),
    ('BIO', _('úspešný riešiteľ - Biologická olympiáda A alebo B - krajské alebo celoštátne kolo')),
    ('CHM', _('úspešný riešiteľ - Chemická olympiáda A alebo B - krajské alebo celoštátne kolo')),
    ('SVOC_MAT', _('úspešný účastník - Stredoškolská odborná činnost odbor 02 matematika, fyzika - celoštátne kolo')),
    ('SVOC_INF', _('úspešný účastník - Stredoškolská odborná činnosť odbor 11 informatika - celoštátne kolo')),
    ('SVOC_BIO', _('úspešný účastník - Stredoškolská odborná činnosť odbor 04 biológia - celoštátne kolo')),
    ('SVOC_CHM', _('úspešný účastník - Stredoškolská odborná činnosť odbor 03 chémia, potravinárstvo - celoštátne kolo')),
    ('TMF', _('úspešný riešiteľ - Turnaj mladých fyzikov - celoštátne kolo'))
]

COMPETITION_YEAR = _('Rok')
COMPETITION_NAME = _('Názov súťaže')
COMPETITION_FURTHER_INFO = _('Ďalšie informácie')
COMPETITION_FURTHER_INFO_DESC = _('V prípade krajského kola do tohto poľa prosím napíšte názov kraja, v ktorom sa daná súťaž konala. V prípade iných kôl do tohto poľa prosím vpíšte akékoľvek iné informácie, ktoré by mohli pomôcť pri identifikácii vášho úspechu.')

COMPETITION_FIRST = _('Úspech na súťaži (1)')
COMPETITION_SECOND = _('Úspech na súťaži (2)')
COMPETITION_THIRD = _('Úspech na súťaži (3)')

EXTERNAL_MATURA_PERCENTILE = _('percentil externej maturity z matematiky')
SCIO_PERCENTILE = _('percentil autorizovanej skúšky z matematiky (SCIO)')
SCIO_DATE = _('dátum vykonania autorizovanej skúšky z matematiky (SCIO)')

MATURA_MAT_GRADE = _('známka z maturity z matematiky')
MATURA_FYZ_GRADE = _('známka z maturity z fyziky')
MATURA_INF_GRADE = _('známka z maturity z informatiky')
MATURA_CHE_GRADE = _('známka z maturity z chémie')
MATURA_BIO_GRADE = _('známka z maturity z biológie')

WILL_TAKE_EXT_MAT = _('plánujem sa zúčastniť externej maturity z matematiky')
WILL_TAKE_SCIO = _('plánujem sa zúčastniť autorizovanej skúšky z matematiky')
WILL_TAKE_MAT_MATURA = _('plánujem maturovať z matematiky')
WILL_TAKE_FYZ_MATURA = _('plánujem maturovať z fyziky')
WILL_TAKE_INF_MATURA = _('plánujem maturovať z informatiky')
WILL_TAKE_BIO_MATURA = _('plánujem maturovať z biológie')
WILL_TAKE_CHE_MATURA = _('plánujem maturovať z chémie')

FURTHER_STUDY_INFO = _('Prospech na strednej škole')

GRADE_FIRST_YEAR = _('koncoročná známka v 1. ročníku / kvinte')
GRADE_SECOND_YEAR = _('koncoročná známka v 2. ročníku / kvarte')
GRADE_THIRD_YEAR = _('koncoročná známka v 3. ročníku / septime')

GRADES_MAT = _('Známky z matematiky')
GRADES_FYZ = _('Známky z fyziky')
GRADES_BIO = _('Známky z biológie')

GRADE_ERR = _('Zle zadaná známka. Akceptované známky sú 1 až 5.')

MENU = [
    (_('ePrihlaska'), 'index'),
    (_('Študijné programy'), 'study_programme'),
    (_('Osobné údaje'), 'personal_info'),
    (_('Informácie o rodičoch'), 'further_personal_info'),
    (_('Adresa'), 'address'),
    (_('Predchádzajúce štúdium'), 'previous_studies'),
    (_('Prijatie bez prijímacích pohovorov'), 'admissions_wavers'),
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

FORGOTTEN_PASSWORD_MAIL = _('Ak by ste chceli zadať nové heslo pre Váš účet, môžete tak urobiť na {}\n\nV inom prípade prosím tento email ignorujte.\n\nS pozdravom,\nhttps://prihlaska.fmph.uniba.sk')

YEAR_ERR = _('Nesprávne zadaná hodnota. Akceptované hodnoty sú v rozsahu od %(min)s po %(max)s')

SEX_CHOICES = [('male', MALE),
               ('female', FEMALE)]
COUNTRY_CHOICES = choices_from_csv(DIR + '/data/staty.csv',
                                       ['id', 'Štát'],
                                       sortby=1,
                                       prepend=['703', '203'])
CITY_CHOICES = choices_from_csv(DIR + '/data/obce.csv',
                                ['id', 'Názov obce', 'Okres'],
                                fmt='{2}, okr. {4}',
                                sortby=1,
                                post_fmt=okres_fixer)

MARITAL_STATUS_CHOICES = choices_from_csv(DIR + '/data/rodinne-stavy.csv',
                                          ['id', 'Rodinný stav'])

HIGHSCHOOL_CHOICES = choices_from_csv(DIR + '/data/skoly.csv',
                                      ['St. šk.', 'Obec', 'Stredná škola',
                                       'Ulica'],
                                      fmt='{2}, {3}, {4}',
                                      sortby=1,
                                      prepend=['XXXXXXX'],
                                      post_fmt=city_formatter)

HS_STUDY_PROGRAMME_CHOICES = choices_from_csv(DIR + '/data/odbory.csv',
                                              ['Odbor - kod',
                                               'Odbor stred. školy'],
                                              fmt='{1} - {2}')

EDUCATION_LEVEL_CHOICES = choices_from_csv(DIR + '/data/vzdelanie.csv',
                                           ['Kód', 'Skrát. popis'],
                                           fmt='({1}) - {3}')

APPLICATION_STATES = [_('rozpracovaná'),
                      _('podaná'),
                      _('vytlačená'),
                      _('spracovaná')]

class ApplicationStates(enum.Enum):
    in_progress = 0
    submitted = 1
    printed = 2
    processed = 3
