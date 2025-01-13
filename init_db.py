from sqlalchemy import text
from eprihlaska import app, db

# https://stackoverflow.com/a/74400992
app.app_context().push()
db.create_all()

# Default alter 'AUTO_INCREMENT' hack for SQLite. Some background info can be
# found on the following links:
# - http://www.vurt.ru/2013/06/sqlite-autoincrement-in-flask-sqlalchemy/
# - https://stackoverflow.com/a/10500177
# - https://stackoverflow.com/a/692871
# - https://www.sqlite.org/autoinc.html
q = "INSERT INTO sqlite_sequence (name, seq) VALUES ('application_form', 1300)"
if db.engine.dialect.name == "mysql":
    q = "ALTER TABLE application_form AUTO_INCREMENT = 1300;"

with db.engine.connect() as conn:
    result = conn.execute(text(q))
    conn.commit()
