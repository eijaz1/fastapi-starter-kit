from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = 'sqlite:///db.sqlite3'
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

### IF USING POSTGRES, UNCOMMENT BELOW 2 LINES AND REMOVE THE ABOVE
### SQLALCHEMY_DATABASE_URL AND engine VARIABLES
SQLALCHEMY_DATABASE_URL = 'postgresql://database_username:database_password@database_hostname/database_name'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()