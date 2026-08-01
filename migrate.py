from sqlalchemy import inspect, text

from extensions import db


def run_migrations():
    """Apply incremental schema changes to an existing SQLite database."""
    inspector = inspect(db.engine)

    # Create all tables first
    db.create_all()

    existing_tables = inspector.get_table_names()

    if "trips" in existing_tables:
        columns = [col["name"] for col in inspector.get_columns("trips")]

        if "trip_type" not in columns:
            db.session.execute(
                text(
                    "ALTER TABLE trips ADD COLUMN trip_type VARCHAR(10) NOT NULL DEFAULT 'group'"
                )
            )
            db.session.commit()
            print("Added trip_type column to trips table.")

    existing_tables = inspector.get_table_names()

    if "expense_splits" in existing_tables:
        es_columns = [col["name"] for col in inspector.get_columns("expense_splits")]
        if "member_id" not in es_columns:
            db.session.execute(text("DROP TABLE IF EXISTS expense_splits"))
            db.session.commit()
            print("Dropped old expense_splits table.")

    if "trip_members" in existing_tables:
        tm_columns = [col["name"] for col in inspector.get_columns("trip_members")]
        if "display_name" not in tm_columns:
            db.session.execute(
                text(
                    "ALTER TABLE trip_members ADD COLUMN display_name VARCHAR(120)"
                )
            )
            db.session.commit()
            print("Added display_name column to trip_members table.")

    


if __name__ == "__main__":
    from app import app

    with app.app_context():
        run_migrations()
        print("Database migrated successfully.")
