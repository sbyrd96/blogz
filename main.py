from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = "secretkey"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    entries = db.relationship('Blog', backref='owner')
       
    def __init__(self, username, password):
        self.username = username
        self.password = password  


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


def text_present(string):
    if string != "":
        return True
    else:
        return False      

def blank_space(string):
    blank_space = " "
    if blank_space in string:
        return True
    else:
        return False  


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blogpage', 'home', 'static', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


# main page, HOME, listing of all users
@app.route("/")
def index():
    owners = User.query.all()
    return render_template('index.html', owners=owners)



# sign up page or register
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        error_present = False

        name_error = "" 
        name_blank_error = ""       
        name_len_error = ""
        password_error = ""
        pass_len_error = ""
        pass_blank_error = ""
        match_error = ""
        mail_error = ""
        usederror = ""
        idusederror = ""


    # unique username check
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            idusederror = "Sorry, but that username is already taken."
            error_present = True

    # username validity check
        if not text_present(username):
            name_error = "This field is required. Please enter a username."
            error_present = True
  
        if blank_space(username):
            name_blank_error = "Blank spaces are not allowed. Please try again."
            error_present = True

        if len(username) > 20 or len(username) < 3:
            name_len_error = "Username must be between 3-20 characters in length."
            error_present = True

    # password validity check
        if not text_present(password):
            password_error = "This field is required. Please enter a password."
            error_present = True

        if blank_space(password):
            pass_blank_error ="Blank spaces are not allowed. Please try again."
            error_present = True

        if len(password) > 20 or len(password) < 3:
            pass_len_error = "Password must be between 3-20 characters in length."           
            error_present = True

    # re-enter password, verification check
        if password != verify:
            match_error = "Please try again. Passwords did not match."
            error_present = True

        if not text_present(verify):
            password_error = "This field is required. Please enter a password."
            error_present = True

    # if no errors, send to newpost page
    if error_present == True:
        return render_template("signup.html", 
        username=username,
        error_present=error_present,
        name_error = name_error,
        name_blank_error = name_blank_error, 
        name_len_error = name_len_error, 
        password_error = password_error, 
        pass_blank_error = pass_blank_error, 
        pass_len_error = pass_len_error, 
        match_error = match_error, 
        mail_error = mail_error,
        idusederror=idusederror)
    else:
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return render_template("newpost.html")


# login page

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html', title="Log In",username=True)

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        
        if users.count() == 1:
            user = users.first()
            
            if password == user.password:
                session['username']=user.username
                return redirect("/newpost")

        flash("Username does not exist or password is incorrect. Please try again.")

        return redirect("/login")



#create a main page that also lists all entries

@app.route('/blog', methods=['POST', 'GET'])
def blogpage():

    if request.method == 'GET':

        if 'id' in request.args:
            blog_id = request.args.get('id')   
            blog_post = Blog.query.filter_by(id = blog_id).first()

            return render_template('single_blog.html', blog_post=blog_post)

        if 'user' in request.args:
            user_id = request.args.get('user')
            allblogs = Blog.query.filter_by(owner_id=user_id)
            return render_template('single_user.html', user_id=user_id, allblogs=allblogs)

            
        else: 
            blogs = Blog.query.all()       
            return render_template('blog.html', blogs=blogs)

    return render_template('newpost.html')



# page to enter text to create a new blogpost

@app.route("/newpost", methods=["POST", "GET"])
def newpost():

    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()  
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body, owner)

        if not text_present(blog_title) and not text_present(blog_body):
            flash("Both a title and a blog entry are required. Please fill both in.")
            return redirect('/newpost', blog_title=blog_title, blog_body=blog_body)

        else:
            db.session.add(new_blog)
            db.session.commit()
            return redirect("/blog?id=" + str(new_blog.id))
    
    else:
        return render_template('/newpost.html') 

@app.route("/logout")
def logout():
    session.clear()
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
