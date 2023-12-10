import base64
import os
from flask import Flask, Response, make_response, render_template, request, redirect, url_for, current_app, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app=Flask(__name__)
app.secret_key='Team18'

current_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///'+ os.path.join(current_dir, "databaseSE.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)
app.app_context().push()

class User(db.Model):
    __tablename__ = 'user'
    UserID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String, nullable=False)
    UserName = db.Column(db.String, unique=True, nullable=False)
    Password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, default='User')


@app.route('/', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        Email = request.form['email']
        UserName = request.form['username']
        Password = request.form['password']
        user = User(Email = Email, UserName = UserName, Password= Password)
        db.session.add(user)
        db.session.commit()

        session['user'] = UserName
        return login()
    
    return render_template("index.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        UserName = request.form['username']
        Password = request.form['password']
        user = User.query.filter_by(UserName = UserName, Password = Password).first()

        return render_template("home.html")
    
    return render_template("home.html")

@app.route('/feedbackpage/<course>', methods=['GET','POST'])
def feedbackpage(course):
    return render_template('feedbackpage.html', course=course)
        
  
if __name__ == "__main__":
    app.run(debug=True)