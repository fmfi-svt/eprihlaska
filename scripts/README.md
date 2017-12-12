
## Ciselnik to CSV

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/572-rodinnyStav.xlsx --filter-NaT='Platnosť do' convert --out-file rodinny_stav.csv id 'Rodinný stav'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/573-staty.xlsx --filter-NaT='Platnosť do' convert --out-file staty.csv id Štát

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/244-obce-nove.xlsx --filter-NaT='Do dátumu' convert --out-file obce.csv 'id' 'Názov obce' 'PSČ'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/109-stredne-skoly.xlsx --filter-NaT='Do dátumu' convert --out-file='skoly.csv' 'St. šk.' 'Obec' 'Stredná škola' 'Ulica'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/715-odborySS.xlsx --filter-NaT='Do dátumu' convert --out-file odbory.csv 'Odbor - kod' 'Odbor stred. školy'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/135-vzdelanie.xlsx --filter-NaT='Do dátumu' convert --out-file vzdelanie.csv 'Kód' 'Typ vzdel.' 'Skrát. popis'
