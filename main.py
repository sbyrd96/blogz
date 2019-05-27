from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = "secretkey"



class User(db.Model):
    userid = db.Column(db.String(120), primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
       
    def __repr__(self):
        return '<User %r>' % self.email



class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    def completed_entry(self):
        if self.title and self.body:
            return True
        else:
            return False

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

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


# main page

@app.route("/")
def index():
    return redirect("/blog")

# sign up page
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        email = request.form['email']
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


    # email validity check
    
        if not is_email(email) and not len(email)==0:
            mail_error = "Please try again. That email address is not in the correct format (@ or .)."
            error_present = True

        if blank_space(email):
            mail_error = "Please try again. That email address is not in the correct format (blank space)."
            error_present = True

        if len(email) > 20 or len(email) < 3 and not len(email)==0:
            mail_error = "Please try again. That email address is not in the correct format (length)." 
            error_present = True

    # if no errors, send to welcome page
    if error_present == True:
        return render_template("signup.html", 
        username=username,
        email=email,
        error_present=error_present,
        name_error = name_error,
        name_blank_error = name_blank_error, 
        name_len_error = name_len_error, 
        password_error = password_error, 
        pass_blank_error = pass_blank_error, 
        pass_len_error = pass_len_error, 
        match_error = match_error, 
        mail_error = mail_error)
    else:
        return render_template("welcome.html", username=username)








# login page

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title="Log In",userid=True)
    elif request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        users = User.query.filter_by(userid=userid)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['userid']=user.userid
                return redirect("/")
        error = "bad username or password"
        return redirect("/login")
    return render_template('login.html', title="Log In",userid=True)





#create a main page that also lists all entries

@app.route('/blog', methods=['POST', 'GET'])
def all_entries():

    entry_id = request.args.get('id')
    if (entry_id):
        entry = Entry.query.get(entry_id)
        return render_template('completed_entry.html', title="My Blog Post", entry=entry)
    else: 
     entries = Entry.query.all()       

    return render_template('blog.html', title="Build a Blog", entries=entries)


# page to enter text to create a new blogpost

@app.route("/newpost", methods=["POST", "GET"])
def new_entry():
    if request.method == 'POST':
        new_entry_title = request.form['title']
        new_entry_body = request.form['body']
        new_entry = Entry(new_entry_title, new_entry_body)

        if new_entry.completed_entry():
            db.session.add(new_entry)
            db.session.commit()
            return redirect("/blog?id=" + str(new_entry.id))

        else:
            flash("Both a title and a blog entry are required. Please fill both in.")
            return render_template('/newpost.html',title="Create New Blog Entry", new_entry=new_entry, new_entry_title=new_entry_title, new_entry_body=new_entry_body)

    else:
        return render_template('/newpost.html',title="Blog Entry")     


if __name__ == '__main__':
    app.run()
