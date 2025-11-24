# scripts/reset_db.py

from app.database import Base, engine
from app import models  # make sure this imports User & Calculation


def main():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Done. Database schema reset.")


if __name__ == "__main__":
    main()
