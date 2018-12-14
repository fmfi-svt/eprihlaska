from eprihlaska import db
db.create_all()

# Default alter 'AUTO_INCREMENT' hack for SQLite. Some background info can be
# found on the following links:
# - http://www.vurt.ru/2013/06/sqlite-autoincrement-in-flask-sqlalchemy/
# - https://stackoverflow.com/a/10500177
# - https://stackoverflow.com/a/692871
# - https://www.sqlite.org/autoinc.html
q = "INSERT INTO sqlite_sequence (name, seq) VALUES ('application_form', 1300)"
if db.engine.dialect.name == 'mysql':
    q = "ALTER TABLE application_form AUTO_INCREMENT = 1300;"

db.engine.execute(q)
db.session.commit()
