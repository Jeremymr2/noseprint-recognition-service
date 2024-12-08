from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

# URL database
database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, echo=True)

# CREATE ALL TABLES
# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)

# DEPENDENCE FOR DATABASE SESSION
def get_session():
    with Session(engine) as session:
        yield session
