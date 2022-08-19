import os
import requests


from flask import Flask,render_template,request,session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text

from flask import jsonify


engine = create_engine(os.getenv("ONLINEDATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")




#to save data in database of signup
@app.route("/rsubmit",methods=["POST"])
def rsubmit():
    userid = request.form.get("userid")
    password= request.form.get("password")
    hash_password = generate_password_hash(password)

    #handle error None
    
    db.execute("INSERT INTO registered_user (userid,hash_password) VALUES (:userid,:hash_password)",
               {"userid": userid, "hash_password":hash_password})
            
    db.commit()
    
    return render_template("success.html",userid=userid)
    



#to fetch data from database of singin
@app.route("/lsubmit",methods=["POST"])
def lsubmit():
    userid = request.form.get("userid")
    password= request.form.get("password")
    hashpassword = generate_password_hash(password)
                      
    #case sensitive
    flight = db.execute("SELECT hash_password FROM registered_user WHERE userid = :userid",
                        {"userid": userid}).fetchone()    

    #here order in check() function is important
    match = check_password_hash(flight[0],password)

    

    if match:
        session["notes"]=[]
        if request.method == "POST": 
            session["notes"].append(userid)
            return render_template("successlogin.html",flight=flight[0],userid=userid)
    
    
    
     
    # handle typerror
    #wrong password
    #user not registered

    

@app.route("/signin")
def signin():        
    return render_template("signin.html")

# task to do

# show loggined:

@app.route("/logout")
def logout():
    if session.get("notes") is not None:
        #session["notes"].pop()
        session.clear()

     # remove all the  session used by the app?
  #  if session[book_id] is not None:
       # session[book_id].pop()
     #  session.clear()

    return render_template("index.html")

#prevent going back 


@app.route("/books")
def books():
    if session.get("notes") is not None:
        return render_template("books.html")


@app.route("/sbooks",methods=["POST"])
def sbooks():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    year = request.form.get("year")

    
    
  #  books= db.execute(text("SELECT * FROM books WHERE isbn LIKE :isbn"),
    #                 {"isbn": f"%{isbn}%"}).fetchall();
  
   # titles = db.execute(text("SELECT * FROM books WHERE title LIKE :title"),
    #                 {"title": f"%{title}%"}).fetchall();
    
    authors = db.execute(text("SELECT * FROM books WHERE author LIKE :author"),
                     {"author": f"%{author}%"}).fetchall();
    
  #  years = db.execute(text("SELECT * FROM books WHERE year LIKE :year"),
   #                  {"year": f"%{year}%"}).fetchall();
    
    # print not found message

    return render_template("found.html",authors=authors)


@app.route("/sbook/<int:book_id>",methods =["GET","POST"])
def sbook(book_id):
    flight = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    
   # fetch isbn?
   
    isbn = flight.isbn
    review = request.form.get("review")
    rating = request.form.get("user")
    #session is of array or list type 
    userid = (session.get("notes"))[0]
    # get value out of session
    
    
    
   #display using loop use fetchall()
   #display directly use fetchone()
    output = db.execute("SELECT * FROM user_review where isbn=:isbn and userid=:userid",
                        {"isbn":isbn,"userid":userid}).fetchone()

    if review and rating is not None:
        t= review
        a=rating
        user_review= db.execute("INSERT INTO user_review (review,rating,isbn,userid) VALUES (:review,:rating,:isbn,:userid)",
                               {"review":review, "rating":rating , "isbn":isbn,"userid":userid})
        db.commit()

   #handle error when user try to insert data again

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"XU1BiKf4hNGYpVBeGnetw": "KEY", "isbns": "9781632168146"})
    data=(res.json())
    
    

        
    return render_template("details.html", flight=flight,book_id=book_id,rating=rating,review=review,res=data)






@app.route("/api/<isbn>")
def api(isbn):


    #check if isbn exist
    # select query

    book = db.execute("SELECT * FROM books where isbn=:isbn",
                        {"isbn":isbn}).fetchone()

    if book is None:
        return jsonify({"error":"invalid isbn"}),422
    
    
    
    #fetch infromation from api
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"XU1BiKf4hNGYpVBeGnetw": "KEY", "isbns":isbn})
    data=(res.json())

    return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": book.isbn,
    "review_count":data["books"][0]["ratings_count"] ,
    "average_score":data["books"][0]["average_rating"]})
    
  







