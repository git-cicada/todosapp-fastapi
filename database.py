from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQL_ALCHEMY_DATABASE_URI = 'sqlite:///./todosapp.db' #sqlite db
#Create a db engine
# engine = create_engine(SQL_ALCHEMY_DATABASE_URI, connect_args={'check_same_thread': False}) 

#POSTGTRSQL DATABASE
SQL_ALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/TodoApplicationDb' #Postgres db


#MYSQL DATABASE
# SQL_ALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rt_123@127.0.0.1:3306/TodoApplicationDatabase' #Mysql db

#Create a db engine
engine = create_engine(SQL_ALCHEMY_DATABASE_URI)


#Bydefault SQLite allow only one thread to connect to it at a time, 
# So we need to pass check_same_thread=False to allow multiple threads to connect to it because FastAPI uses multiple threads to handle requests. 
# can send multiple requests at the same time.

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() #A database object





