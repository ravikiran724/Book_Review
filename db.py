from sqlalchemy import ccreate_engine
from sqlalchemy.orm imoprt sessionmaker,scoped_session()
import os
engine=create_engine(os.getenv('DATABASE_URL'))
db=scoped_session(sessionmaker(bind=engine))
def main():
    db.execute('insert into Login_details (user_name,password) values (:usr,:pass)',{'usr':usr,'pass':passs})
    print("Added")
    db.commit()
    