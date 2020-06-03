import os

from flask import *
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template('home.html')
@app.route("/login",methods=["POST","GET"])
def check():
    usr=request.form.get('user')
    passs=request.form.get('pass')
    if(usr=="" or passs==""):
        flash("Enter Login Details")
        return render_template('home.html')
    res=db.execute('select * from login where user_name=:user and password=:pass',{'user':usr,'pass':passs}).fetchone()
    if(res==None):
        flash("Incorrct Details")
    else:
        mess='Login Success'
        session['user_id']=usr
        ans=db.execute('select * from books').fetchall()
        return render_template('search.html',data=ans)
    db.commit() 
    return render_template('home.html')
@app.route("/r",methods=["GET"])
def r():
    return render_template('register.html')
@app.route("/register",methods=["POST"])
def register():
    usr=request.form.get('user')
    passs=request.form.get('pass')
    tpass=request.form.get('tpass')
    res=db.execute('select * from login where user_name=:user',{'user':usr,'pass':passs}).fetchone()
    if(res):
        flash("User Name Already Exists")
        return render_template('register.html')
    if(passs==tpass):
        db.execute('insert into login (user_name,password) values (:usr,:pass)',{'usr':usr,'pass':passs})
        print("Added")
        db.commit()
        mess="Successfully Registered"
        return render_template('home.html',m=mess)
    else:
        flash("Password didn't match")
        return render_template('register.html')
@app.route("/sear",methods=["POST"])
def sear():
    isb=request.form.get('isbn')
    title=request.form.get('title')
    author=request.form.get('author')
    if(isb is None):
        isb=""
    if(title is None):
        title=""
    if(author is None):
        author=""
    if(isb=="" and title=="" and author==""):
        flash("Enter a Value in Search Field")
        return render_template('search.html')
    isb='%'+isb+'%'
    title='%'+title+'%'
    author='%'+author+'%'
    chk=db.execute('select * from books where isbn like :isb and title like :title and author like :author',{'isb':isb,'title':title,'author':author}).fetchone()
    if(chk is None):
        return "<h1>No Such Book</h1>"
    ser=db.execute('select * from books where isbn like :isb and title like :title and author like :author',{'isb':isb,'title':title,'author':author}).fetchall()
    return render_template('view.html',data=ser)
@app.route('/bookk',methods=["POST"])
def bookk():
    isb=request.form.get('id')
    ans=db.execute('select * from books where isbn=:id',{'id':isb}).fetchall()
    review=db.execute('select * from reviews where isbn=:id',{'id':isb}).fetchall()
    give_r=db.execute('select * from reviews where isbn=:id and user_id=:uid',{'id':isb,'uid':session['user_id']}).fetchone()
    res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "anKyCfnpJiYHnlTkOD7Q", "isbns": isb})
    if(give_r is None):
        var=True
    else:
        var=False
    return render_template('bookk.html',dtat=ans,reviews=review,gr=var,rc=res.json()['books'][0]['work_ratings_count'],avg=res.json()['books'][0]['average_rating'])
@app.route('/review',methods=["POST","GET"])
def review():
    if session.get('user_id'):
        review=request.form.get('review')
        sc=request.form.get('re')
        isbn=request.form.get('isbn')
        sc=int(sc)
        db.execute('insert into reviews (isbn,review,user_id,rating) values (:isbn,:review,:user_id,:rating)',{'isbn':isbn,'review':review,'user_id':session['user_id'],'rating':sc})
        db.commit()
        ans=db.execute('select * from books where isbn=:id',{'id':isbn}).fetchall()
        review=db.execute('select * from reviews where isbn=:id',{'id':isbn}).fetchall()
        give_r=db.execute('select * from reviews where isbn=:id and user_id=:uid',{'id':isbn,'uid':session['user_id']}).fetchone()
        if(give_r is None):
            var=True
        else:
            var=False
        res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "anKyCfnpJiYHnlTkOD7Q", "isbns": isbn})
        return render_template('bookk.html',dtat=ans,reviews=review,gr=var,rc=res.json()['books'][0]['work_ratings_count'],avg=res.json()['books'][0]['average_rating'])
    else:
        ms='Please Login'
        return render_template('error.html',msg=ms)

@app.route('/api/<string:isbn>')
def api(isbn):
    ans=db.execute('select * from books where isbn=:id',{'id':isbn}).fetchone()
    if(ans is None):
        return "<h1>Invalid ISBN Number</h1>"
    else:
        review=db.execute('select round(avg(rating)) as aavg from reviews where isbn=:id',{'id':isbn}).fetchone()
        revieww=db.execute('select count(*) as cnt from reviews where isbn=:id',{'id':isbn}).fetchone()
        if(review is None):
            ms='Invalid ISBN Number'
            return render_template('error.html',msg=ms)
        return jsonify({
            'title':ans.title,
            'author':ans.author,
            'year':ans.year,
            'isbn':ans.isbn,
            'review_count':revieww.cnt,
            'average_score':review.aavg
        })
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
    