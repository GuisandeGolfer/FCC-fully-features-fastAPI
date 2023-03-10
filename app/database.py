from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQL_ALCHEMY_DB_URL = "postgresql://postgres:Diegito23!@localhost/fastAPI"

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
