import base64
import csv
from datetime import datetime
import io
import os
from flask import Flask, Response, make_response, render_template, request, redirect, send_file, url_for, current_app, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload
import matplotlib.pyplot as plt

app = Flask(__name__)

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
    Email = db.Column(db.String, nullable=False, unique=True)
    UserName = db.Column(db.String, unique=True, nullable=False)
    Password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, default='User')
    UserDetailsR = db.relationship('UserDetails', backref='user', lazy=True)
    FeedbackR = db.relationship('Feedback', backref='user', lazy=True)
    CourseIntrestR = db.relationship('CourseInterest', backref='user', lazy=True)
    PastCourseR = db.relationship('PastCourse', backref='user', lazy=True)
    FutureGoalsR = db.relationship('FutureGoals', backref='user', lazy=True)

class UserDetails(db.Model):
    __tablename__ = 'userdetails'
    Email = db.Column(db.String, db.ForeignKey('user.Email'), nullable=False, primary_key=True)
    Name = db.Column(db.String, nullable=False)
    RollNo = db.Column(db.String, nullable=False)
    Level = db.Column(db.String, nullable=False)
    DoB = db.Column(db.String, nullable=False)
    ProfilePicture = db.Column(db.LargeBinary, nullable=True)
    JoiningTerm = db.Column(db.String, nullable=False)
    CurrentCGPA = db.Column(db.Integer, nullable=False)

class Courses(db.Model):
    __tablename__ = 'courses'
    CourseID = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement= True)
    CourseName = db.Column(db.String, nullable=False)
    CourseCredit = db.Column(db.Integer, nullable=False)
    CourseProfessor = db.Column(db.String, nullable=False)
    Courselink = db.Column(db.String, nullable=False)
    CourseDescription= db.Column(db.String, nullable=False)
    CourseLevel = db.Column(db.String, nullable=False)
    CourseRating = db.Column(db.Integer, nullable=False, default=0)
    FeedbackR = db.relationship('Feedback', backref='courses', lazy=True)
    CourseIntrestR = db.relationship('CourseInterest', backref='courses', lazy=True)
    PastCourseR = db.relationship('PastCourse', backref='courses', lazy=True)
    FutureGoalsR = db.relationship('FutureGoals', backref='courses', lazy=True)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    FeedbackID = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement= True)
    Feedback = db.Column(db.String, nullable=False)
    Timestamp = db.Column(db.String, nullable=False)
    Ratings = db.Column(db.String, nullable = False)
    UserID = db.Column(db.String, db.ForeignKey('user.UserID'), nullable=False)
    CourseID =db.Column(db.String, db.ForeignKey('courses.CourseID'), nullable=False)
    PastCourseR = db.relationship('PastCourse', backref='feedback', lazy=True)

class CourseInterest(db.Model):
    __tablename__ = 'courseinterest'
    CourseInterestID = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement= True)
    UserID = db.Column(db.String, db.ForeignKey('user.UserID'), nullable=False)
    CourseID =db.Column(db.String, db.ForeignKey('courses.CourseID'), nullable=False)

class PastCourse(db.Model):
    __tablename__ = 'pastcourse'
    PastCourseID = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement= True)
    CompletionTerm = db.Column(db.String, nullable=False)
    CGPA = db.Column(db.String, nullable=False)
    UserID = db.Column(db.String, db.ForeignKey('user.UserID'), nullable=False )
    CourseID =db.Column(db.String, db.ForeignKey('courses.CourseID'), nullable=False )
    FeedbackID = db.Column(db.String, db.ForeignKey('feedback.FeedbackID'), nullable=True)

class FutureGoals(db.Model):
    __tablename__ = 'futuregoals'
    FutureGoalID = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement= True)
    Detail = db.Column(db.String, nullable=False)
    CompletionTill = db.Column(db.String, nullable=False)
    UserID = db.Column(db.String, db.ForeignKey('user.UserID'), nullable=False)
    CourseID =db.Column(db.String, db.ForeignKey('courses.CourseID'), nullable=False)

@app.route('/updateprofile', methods=['GET', 'POST'])
def updateprofile():
    if request.method == 'POST':
        user = User.query.filter_by(UserName=session.get('user')).first()
        print(session.get('user'))
        userdetails = UserDetails.query.filter_by(Email=user.Email).first()

        if 'profile_picture' in request.files:

            image_data = request.files['profile_picture'].read()
            userdetails.ProfilePicture = image_data
            db.session.commit()

            flash("Profile Picture Update Successfully")
            return profile()


@app.route('/', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        Email = request.form['email']
        UserName = request.form['username']
        Password = request.form['password']
        if UserDetails.query.filter_by(Email=Email).first():
            user = User(Email = Email, UserName = UserName, Password= Password)
            db.session.add(user)
            db.session.commit()
         
            return login()
        else:
            flash("User's Email not Found")
            return render_template("index.html")
    
    return render_template("index.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        UserName = request.form['username']
        Password = request.form['password']
        user = User.query.filter_by(UserName = UserName, Password = Password).first()
        if user:
             session['user'] = UserName
             print(session.get('user'))
             courses = Courses.query.all()
             image_data = profiledata()
             flash("Login Successful")
             return render_template("home.html", courses=courses, image_data=image_data, user=user)
        else:
            flash("Invalid Credentials...Please Login with correct username & password")
            return render_template("index.html")
    user = User.query.filter_by(UserName=session.get('user')).first()
    image_data=profiledata()
    courses = Courses.query.all()
    return render_template("home.html", courses=courses, image_data=image_data, user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)  
    flash("Logged Out Successfully!!")
    return render_template("index.html")

@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    if request.method=='POST':
        UserName = request.form['username']
        Password = request.form['password']
        user = User.query.filter_by(UserName = UserName, Password = Password, Role = 'Admin').first()
        if user:
            session['user'] = UserName
            courses = Courses.query.all()
            l = []
            a=0
            for i in range(len(courses)):
                a= 3*i
                if a <= len(courses):
                    l.append(a)
            print(session.get('user'))
            users = User.query.count()
            course_names = [course.CourseName for course in courses]
            ratings = [course.CourseRating for course in courses]

            fig, ax = plt.subplots(figsize=(5, 5.5))  
            bars = ax.barh(course_names, ratings, color='#ffdd07')  
            ax.set_xlabel('Rating')
            ax.set_title('Ratings vs Course Name') 
            ax.set_yticks([])

        
            ax.set_xticks([1, 2, 3, 4, 5]) 
            ax.set_xlim(0, 5) 
            ax.tick_params(axis='both', which='both', labelsize=8)  
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            
            for bar, course_name in zip(bars, course_names):
                ax.text(bar.get_width()+0.1, bar.get_y() + bar.get_height() / 2, course_name, ha='left', va='center', fontsize=8)

    
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            stats = base64.b64encode(img.getvalue()).decode()
            return render_template("admindashboard.html", user=user, courses=courses, l=l, users=users, stats=stats)
        else:
            flash("Invalid username and password. Login with correct credentials of Admin!!")
            return render_template('index.html')

@app.route('/uploaduserdata', methods=['GET', 'POST'])
def uploaduserdata():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
                
                text_stream = io.TextIOWrapper(file.stream, encoding='utf-8')
                csv_data = csv.reader(text_stream)
                next(csv_data)
                for row in csv_data:
                    user_details = UserDetails(
                        Email=row[0],
                        Name=row[1],
                        RollNo=row[2],
                        Level=row[3],
                        DoB=row[4],
                        JoiningTerm=row[5],
                        CurrentCGPA=row[6]
                    )
                    db.session.add(user_details)

                db.session.commit()

                flash("Student's Data Added Successfully")
                return admindashboard()

@app.route('/feedbackpage/<CourseID>', methods=['GET','POST'])
def feedbackpage(CourseID):
    user = User.query.filter_by(UserName = session.get('user')).first()
    userdetails = UserDetails.query.filter_by(Email=user.Email).first()
    course = Courses.query.filter_by(CourseID=CourseID).first()
    image_data = profiledata()
    feedbacks = (Feedback.query
             .join(User)
             .options(joinedload(Feedback.user))
             .filter(Feedback.CourseID == CourseID, Feedback.UserID == User.UserID)
             .all())
    print(feedbacks)
    studentfeedback = Feedback.query.filter_by(UserID= user.UserID, CourseID=CourseID).first()
    if studentfeedback:
        feedbacks  = Feedback.query.filter(and_(Feedback.CourseID == CourseID,Feedback.UserID != user.UserID)).all()
        l = []
        a=0
        for i in range(1,len(feedbacks)):
            a= 3*i -1
            if a <= len(feedbacks):
                l.append(a)
            else:
                if l[-1] != len(feedbacks):
                    l.append(len(feedbacks))
                    break
        print(l)
        print(feedbacks)
        return render_template('feedbackpage.html', course=course, studentfeedback=studentfeedback, feedbacks=feedbacks, l=l, user=user,userdetails=userdetails, image_data = image_data)
    
    else:
        l = []
        a=0
        for i in range(len(feedbacks)):
            a= 3*i
            if a <= len(feedbacks):
                l.append(a)
            else:
                if l[-1] != len(feedbacks):
                    l.append(len(feedbacks))
                    break
        print(l)
        return render_template('feedbackpage.html', course=course, feedbacks=feedbacks, l=l, image_data=image_data,user=user,userdetails=userdetails)


@app.route('/profile', methods=['GET','POST'])
def profile():
    UserName = session.get('user')
    user = User.query.filter_by(UserName = UserName).first()
    userdetails = UserDetails.query.filter_by(Email=user.Email).first()
    courses = Courses.query.all()
    pastcourse = (PastCourse.query.join(Courses).join(Feedback, isouter=True).options(joinedload(PastCourse.courses)).options(joinedload(PastCourse.feedback)).filter(PastCourse.UserID == user.UserID)).all()
    courseinterest = (CourseInterest.query.join(Courses).options(joinedload(CourseInterest.courses)).filter(CourseInterest.UserID == user.UserID)).all()
    futuregoal = (FutureGoals.query.join(Courses).options(joinedload(FutureGoals.courses)).filter(FutureGoals.UserID == user.UserID)).all()
    Terms = ["Jan 2022", "May 2022", "Sep 2022", "Jan 2023", "May 2023"]

    
    if userdetails and userdetails.ProfilePicture:
        image_data = profiledata()
        return render_template('profile.html', user=user, userdetails=userdetails, futuregoal=futuregoal, pastcourse=pastcourse, courseinterest=courseinterest, courses = courses, Terms=Terms, image_data=image_data)

      
    return render_template('profile.html', user=user, userdetails=userdetails, futuregoal=futuregoal, pastcourse=pastcourse, courseinterest=courseinterest, courses = courses, Terms=Terms)

def profiledata():
    user = User.query.filter_by(UserName = session.get('user')).first()
    userdetails = UserDetails.query.filter_by(Email=user.Email).first()
    if userdetails and userdetails.ProfilePicture:
        image_data = base64.b64encode(userdetails.ProfilePicture).decode('utf-8')
        return image_data

@app.route('/addcourse', methods=['GET','POST'])
def addcourse():
    if request.method == 'POST':
        course = Courses(
        CourseName = request.form['coursename'],
        CourseCredit =  request.form['credit'],
        CourseProfessor = request.form['professor'],
        Courselink = request.form['link'],
        CourseDescription= request.form['description'],
        CourseLevel = request.form['level'])
        db.session.add(course)
        db.session.commit()

        flash("Course Added Successfully!!")
        return admindashboard()
    

@app.route('/pastcourse', methods=['GET','POST'])
def pastcourse():
    if request.method == 'POST':
        user = User.query.filter_by(UserName = session.get('user')).first()
        if PastCourse.query.filter_by(CourseID = request.form['course'], UserID = user.UserID).first():
           flash("Data alredy exist!!")
           return profile()
        if request.form['feedback'] and str(request.form.getlist("rate"))[2:3]:
            feedback = Feedback(
                Feedback= request.form['feedback'],
                Timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                UserID = user.UserID,
                CourseID = request.form['course'],
                Ratings = str(request.form.getlist("rate"))[2:3]
            )
            db.session.add(feedback)
            db.session.commit()
       
            pastcourse = PastCourse(
            CourseID = request.form['course'],
            UserID =  user.UserID,
            CGPA = request.form['cgpa'],
            CompletionTerm = request.form['term'],
            FeedbackID = feedback.FeedbackID
            )
            db.session.add(pastcourse)
            db.session.commit()

            ratings = Feedback.query.filter_by(CourseID=request.form['course']).all()
            sum =0
            count = 0
            for r in ratings:
                sum+=r.Ratings
                count+=1
            if count !=0:
                course = Courses.query.filter_by(CourseID=request.form['course']).first()
                course.CourseRating = sum//count
                db.session.commit()


        elif Feedback.query.filter_by(CourseID = request.form['course'], UserID=user.UserID).first():
            f = Feedback.query.filter_by(CourseID = request.form['course'], UserID=user.UserID).first()
            pastcourse = PastCourse(
            CourseID = request.form['course'],
            UserID =  user.UserID,
            CGPA = request.form['cgpa'],
            CompletionTerm = request.form['term'],
            FeedbackID = f.FeedbackID
            )
            db.session.add(pastcourse)
            db.session.commit()
        else:
            pastcourse = PastCourse(
            CourseID = request.form['course'],
            UserID =  user.UserID,
            CGPA = request.form['cgpa'],
            CompletionTerm = request.form['term'],
            )
            db.session.add(pastcourse)
            db.session.commit()

        flash("Your Past perfornmance added successfully!!")
        return profile()
        
@app.route('/courseinterest', methods=['GET','POST'])
def courseinterest():
    if request.method == 'POST':
        user = User.query.filter_by(UserName = session.get('user')).first()
        if CourseInterest.query.filter_by(UserID=user.UserID, CourseID = request.form['course']).first():
            return profile()
        else:
            intrest= CourseInterest(
                CourseID = request.form['course'],
                UserID = user.UserID
            )
            db.session.add(intrest)
            db.session.commit()
            flash("Your Course Intrest added successfully!!")
            return profile()

@app.route('/futuregoal', methods=['GET','POST'])
def futuregoal():
    if request.method == 'POST':
        user = User.query.filter_by(UserName = session.get('user')).first()
        if FutureGoals.query.filter_by(CourseID = request.form['course'], UserID = user.UserID).first():
            return profile()
        else:
            goal = FutureGoals(
                CourseID = request.form['course'],
                UserID = user.UserID,
                Detail = request.form['comment'],
                CompletionTill = request.form['term']
            )
            db.session.add(goal)
            db.session.commit()
            flash("Your Duture Goal added successfully!!")
            return profile()
        
@app.route('/updatepastcourse/<PastCourseID>', methods=['GET','POST'])
def updatepastcourse(PastCourseID):
    if request.method == 'POST':
        Term = request.form['term']
        CGPA = request.form['cgpa']
        pcourse = PastCourse.query.filter_by(PastCourseID=PastCourseID).first()
        pcourse.CompletionTerm = Term
        pcourse.CGPA = CGPA
        db.session.commit()

        flash("Your Past perfornmance Updated successfully!!")
        return profile()

        
@app.route('/deletegoal/<GoalID>', methods=['GET','POST'])
def deletegoal(GoalID):
    db.session.delete(FutureGoals.query.filter_by(FutureGoalID=GoalID).first())
    db.session.commit()
    flash("Your Future Goal Deleted successfully!!")
    return profile()

@app.route('/deleteinterest/<InterestID>', methods=['GET','POST'])
def deleteinterest(InterestID):
    db.session.delete(CourseInterest.query.filter_by(CourseInterestID=InterestID).first())
    db.session.commit()
    flash("Your Course Interest Deleted successfully!!")
    return profile()

@app.route('/deletepastcourse/<PastCourseID>', methods=['GET','POST'])
def deletepastcourse(PastCourseID):
    db.session.delete(PastCourse.query.filter_by(PastCourseID=PastCourseID).first())
    db.session.commit()
    flash("Your Past perfornmance Deleted successfully!!")
    return profile()

@app.route('/seemorepath', methods=['GET','POST'])
def seemorepath():
    user = User.query.filter_by(UserName = session.get('user')).first()
    image_data = profiledata()
    return render_template("seemorepath.html" , image_data=image_data, user=user)

@app.route('/feedback/<CourseID>', methods=['GET','POST'])
def feedback(CourseID):
    if request.method == 'POST':
        user = User.query.filter_by(UserName = session.get('user')).first()
        feedback = Feedback(
            Feedback= request.form['feedback'],
            Timestamp = datetime.now().strftime('%d/%m/%Y at  %H:%M'),
            UserID = user.UserID,
            CourseID = CourseID,
            Ratings = str(request.form.getlist("rate"))[2:3]
        )
        db.session.add(feedback)
        p = PastCourse.query.filter_by(UserID=user.UserID, CourseID = CourseID).first()
        if p:
            p.FeedbackID = feedback.FeedbackID
        db.session.commit()

        ratings = Feedback.query.filter_by(CourseID=CourseID).all()
        sum =0
        count = 0
        for r in ratings:
            sum+=r.Ratings
            count+=1
        if count !=0:
            course = Courses.query.filter_by(CourseID=CourseID).first()
            course.CourseRating = sum//count
            db.session.commit()

        flash("Feedback Added successfully!!")
        return feedbackpage(CourseID)
    
@app.route('/deletefeedback/<FeedbackID>', methods=['GET','POST'])
def deletefeedback(FeedbackID):
    feedback = Feedback.query.filter_by(FeedbackID= FeedbackID).first()
    CourseID = feedback.CourseID
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback Deleted successfully!!")
    return feedbackpage(CourseID)

@app.route('/updatefeedback/<FeedbackID>', methods=['GET','POST'])
def updatefeedback(FeedbackID):   
    if request.method =="POST":
        feedback= Feedback.query.filter_by(FeedbackID= FeedbackID).first()
        feedback.Feedback = request.form['feedback']
        feedback.Ratings = str(request.form.getlist("rate"))[2:3]
        feedback.Timestamp =datetime.now().strftime('%d/%m/%Y at %H:%M')
        db.session.commit()

        ratings = Feedback.query.filter_by(CourseID=feedback.CourseID).all()
        sum =0
        count = 0
        for r in ratings:
            sum+=r.Ratings
            count+=1
        if count !=0:
            course = Courses.query.filter_by(CourseID=feedback.CourseID).first()
            course.CourseRating = sum//count
            db.session.commit()

        flash("Feedback Updated successfully!!")
        return feedbackpage(feedback.CourseID)

@app.route('/editcourse/<CourseID>', methods=['GET','POST'])
def editcourse(CourseID):   
    if request.method =="POST":
        course = Courses.query.filter_by(CourseID=CourseID).first()
        course.CourseName = request.form['coursename']
        course.CourseCredit =  request.form['credit']
        course.CourseProfessor = request.form['professor']
        course.Courselink = request.form['link']
        course.CourseDescription= request.form['description']
        course.CourseLevel = request.form['level']
        db.session.commit()
        flash("Course Updated successfully!!")
        return admindashboard()
    
@app.route('/deletecourse/<CourseID>', methods=['GET','POST'])
def deletecourse(CourseID):  
    course = Courses.query.filter_by(CourseID=CourseID).first()
    feedbacks = Feedback.query.filter_by(CourseID=CourseID).all()
    pastcourse = PastCourse.query.filter_by(CourseID=CourseID).all()
    courseinterest = CourseInterest.query.filter_by(CourseID=CourseID).all()
    futuregoal = FutureGoals.query.filter_by(CourseID=CourseID).all()
    for f in feedbacks:
        db.session.delete(f)
        db.session.commit()
    for pc in pastcourse:
        db.session.delete(pc)
        db.session.commit()
    for ci in courseinterest:
        db.session.delete(ci)
        db.session.commit()
    for fg in futuregoal:
        db.session.delete(fg)
        db.session.commit()
    db.session.delete(course)
    db.session.commit()

    flash("Course Deleted successfully!!")
    return admindashboard()

def admindashboard():
    user = User.query.filter_by(UserName=session.get('user')).first()
    if user:
        courses = Courses.query.all()
        l = []
        a=0
        for i in range(len(courses)):
            a= 3*i
            if a <= len(courses):
                l.append(a)
        users = User.query.count()
        course_names = [course.CourseName for course in courses]
        ratings = [course.CourseRating for course in courses]

        fig, ax = plt.subplots(figsize=(5, 5.5))  
        bars = ax.barh(course_names, ratings, color='#ffdd07')  
        ax.set_xlabel('Rating')
        ax.set_title('Ratings vs Course Name') 
        ax.set_yticks([])

       
        ax.set_xticks([1, 2, 3, 4, 5]) 
        ax.set_xlim(0, 5) 
        ax.tick_params(axis='both', which='both', labelsize=8)  
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        ax.spines['left'].set_visible(True)
        
        for bar, course_name in zip(bars, course_names):
            ax.text(bar.get_width()+0.1, bar.get_y() + bar.get_height() / 2, course_name, ha='left', va='center', fontsize=8)

   
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        stats = base64.b64encode(img.getvalue()).decode()
        return render_template("admindashboard.html", user=user, courses=courses, l=l, users=users, stats=stats)


   

if __name__ == "__main__":
    app.run(debug=True)