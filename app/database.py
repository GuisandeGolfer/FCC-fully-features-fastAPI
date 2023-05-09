from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# The file that helps us connect/create a database engine on our local machine and eventually in our cloud service through Docker

SQL_ALCHEMY_DB_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(
    SQL_ALCHEMY_DB_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# all models that we define will extend this base class.


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
