
## Ciselnik to CSV

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/572-rodinnyStav.xlsx --filter-NaT='Platnosť do' convert --out-file rodinny_stav.csv id 'Rodinný stav'

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/573-staty.xlsx --filter-NaT='Platnosť do' convert --out-file staty.csv id Štát

    $ python3 ciselnik_to_csv.py --file ../eprihlaska/data/244-obce-nove.xlsx --filter-NaT='Do dátumu' convert --out-file obce.csv 'id' 'Názov obce' 'PSČ'
