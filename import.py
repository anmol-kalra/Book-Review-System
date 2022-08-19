import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("ONLINEDATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def main():

    f = open("books.csv")
    reader = csv.reader(f)

    for row in reader:
        db.execute("INSERT INTO  books (isbn,title,author,year) VALUES (:w,:x,:y,:z)",
                   {"w":row[0],"x":row[1],"y":row[2],"z":row[3]})
                   
        print(f"Added book  {row[0]} {row[1]} by {row[2]} published in {row[3]}")

    db.commit()

        
if __name__ == "__main__":
    main()


