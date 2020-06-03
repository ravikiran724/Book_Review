import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
import os
engine=create_engine(os.getenv('DATABASE_URL'))
db=scoped_session(sessionmaker(bind=engine))
def main():
    f=open('books.csv')
    cn=0
    read=csv.reader(f)
    for a,b,c,d in read:
        db.execute('insert into books (isbn,title,author,year) values (:a,:b,:c,:d)',{'a':a,'b':b,'c':c,'d':d})
        print(cn)
        cn=cn+1
    db.commit()
    print("success")
main()