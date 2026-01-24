#!/usr/bin/env python3
import argparse
import sys

from sqlalchemy import text

from eprihlaska import app, db


def reset_autoincrement():
    q = "INSERT INTO sqlite_sequence (name, seq) VALUES ('application_form', 1300)"
    if db.engine.dialect.name == "mysql":
        q = "ALTER TABLE application_form AUTO_INCREMENT = 1300;"

    with db.engine.begin() as conn:
        conn.execute(text(q))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wipe and recreate the application database for a new season."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt.",
    )
    args = parser.parse_args()

    app.app_context().push()
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "<unknown>")

    print(f"Target DB: {uri}")
    if not args.yes:
        confirm = input("This will ERASE ALL DATA. Type WIPE to continue: ").strip()
        if confirm != "WIPE":
            print("Aborted.")
            return 1

    print("Dropping all tables...")
    db.drop_all()
    print("Creating tables...")
    db.create_all()

    try:
        reset_autoincrement()
    except Exception as exc:  # pragma: no cover - best-effort safety
        print(f"Warning: could not reset autoincrement: {exc}", file=sys.stderr)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
