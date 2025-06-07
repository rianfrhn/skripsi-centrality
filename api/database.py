
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
user     = os.getenv("MYSQLUSER")
password = os.getenv("MYSQLPASSWORD")
host     = os.getenv("MYSQLHOST")
port     = os.getenv("MYSQLPORT", 3306)
db       = os.getenv("MYSQLDATABASE")

URL_DATABASE = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(URL_DATABASE, echo=True)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

Base = declarative_base()

