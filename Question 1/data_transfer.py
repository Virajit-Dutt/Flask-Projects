from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
import os

sqlite_engine = create_engine('sqlite:///./instance/test.db')
SQLiteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SQLiteSession()

u = 'root'
password = ''
host = 'localhost'
database = 'test'

mysql_engine = create_engine(f'mysql+pymysql://{u}:{password}@{host}/{database}')
MySQLSession = sessionmaker(bind=mysql_engine)
mysql_session = MySQLSession()

users = sqlite_session.query(User).all()

print(users)

for user in users:
    mysql_session.add(User(id=user.id, username=user.username, password_hash=user.password_hash, role=user.role))

mysql_session.commit()

sqlite_session.close()
mysql_session.close()