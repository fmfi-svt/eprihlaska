
## Ciselnik to CSV

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/572-rodinnyStav.xlsx --filter-NaT='Platnosť do' convert --out-file rodinny_stav.csv id 'Rodinný stav'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/573-staty.xlsx --filter-NaT='Platnosť do' convert --out-file staty.csv id Štát

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/109-stredne-skoly.xlsx --filter-NaT='Do dátumu' convert --out-file='skoly.csv' 'St. šk.' 'Obec' 'Stredná škola' 'Ulica'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/715-odborySS.xlsx --filter-NaT='Do dátumu' convert --out-file odbory.csv 'Odbor - kod' 'Odbor stred. školy'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/135-vzdelanie.xlsx --filter-NaT='Do dátumu' convert --out-file vzdelanie.csv 'Kód' 'Typ vzdel.' 'Skrát. popis'

    $ python3 ciselnik_obce_to_csv.py  --file ../eprihlaska/data/244-obce-nove.xlsx --filter-NaT='Do dátumu' convert --out-file obce.csv 'id' 'Názov obce' 'PSČ' 'Okres'

## Ciselnik to CSV in 2019

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/PK_FMFI_Ciselniky.xlsx --sheet 572 --filter-NaT='Platnosť do' convert --out-file ../eprihlaska/data/rodinne-stavy.csv id 'Rodinný stav'

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/PK_FMFI_Ciselniky.xlsx --sheet 573 --filter-NaT='Platnosť do' convert --out-file ../eprihlaska/data/staty.csv  id Štát

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/PK_FMFI_Ciselniky.xlsx  --sheet 109 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/skoly.csv 'St. šk.' 'Obec' 'Stredná škola' 'Ulica'

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/PK_FMFI_Ciselniky.xlsx  --sheet 715 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/odbory.csv  'Odbor - kod' 'Odbor stred. školy'

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/PK_FMFI_Ciselniky.xlsx --sheet 135 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/vzdelanie.csv  'Kód' 'Typ vzdel.' 'Skrát. popis'

        $ python3 ciselnik_obce_to_csv.py  --file ../eprihlaska/data/PK_FMFI_Ciselniky.xlsx --sheet 244 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/obce.csv  'id' 'Názov obce' 'PSČ' 'Okres'

## Ciselnik to CSV in 2022

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/Ciselniky_PK_2022_01_10.xlsx  --sheet 109 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/skoly.csv 'St. šk.' 'Obec' 'Stredná škola' 'Ulica'

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/Ciselniky_PK_2022_01_10.xlsx  --sheet 715 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/odbory.csv  'Odbor - kod' 'Odbor stred. školy'

        $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/Ciselniky_PK_2022_01_10.xlsx --sheet 714 convert --out-file ../eprihlaska/data/ss-odbor-map.csv  'St. šk.' 'Odbor - kod'

        $ python3 ciselnik_obce_to_csv.py  --file ../eprihlaska/data/Ciselniky_PK_2022_01_10.xlsx --sheet 244 --filter-NaT='Do dátumu' convert --out-file ../eprihlaska/data/obce.csv  'id' 'Názov obce' 'PSČ' 'Okres'
