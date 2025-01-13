# ePrihlaska

A web app that handles the process of applying to the
[Faculty of Mathematics, Physics and Informatics](https://fmph.uniba.sk/)
of the Comenius University in Bratislava.

## How do I try this out?

- [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- Run `uv sync`

Copy `config-sample.py` to `config.py`.
At this point you should most probably change the config options in `config.py`
as you see fit. Once that is done, the DB can be created by running

- `uv run python init_db.py`

You can then start the local version of this app by running

- `uv run python run.py`

If you are changing styles, recompile them by running

- `sass --watch main.scss:main.css`

inside `eprihlaska/static/styles` folder
