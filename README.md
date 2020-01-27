# ePrihlaska

## How do I try this out?

- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`

Copy `config-sample.py` to `config.py`.
At this point you should most probably change the config options in `config.py`
as you see fit. Once that is done, the DB can be created by running

- `python3 init_db.py`

You can then start the local version of this app by running

- `python3 run.py`

If you are changing styles, recompile them by running
- `sass --watch main.scss:main.css`
inside /eprihlaska/static/styles folder

Note that this application requires Python 3.
