from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


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


# main page

@app.route("/")
def index():
    return redirect("/blog")


#create a main page that also lists all entries

@app.route('/blog', methods=['POST', 'GET'])
    def all_entries():
        entry_id = request.args.get('id')
        if (entry_id):
            Entry.query.get(entry_id)
            return render_template('blog.html', title="Blog Post", entry=entry)


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

            url = "/blog?id=" + str(new_entry.id)
            return redirect(url)
        else:
            flash("Both a title and a blog entry are required. Please fill both in.")
            return render_template('/newentry.html',title="Create New Blog Entry", new_entry=new_entry, new_entry_title=new_entry_title, new_entry_body=new_entryk_body)

    return render_template('/completed_entry.html',title="Blog Entry", new_entry_title=new_entry_body, new_entry_title=new_entry_title)     


# create new page that lists the selected (or newest) entry

@app.route("/completed_entry, methods=["GET"])
def completed_entry():
    completed_entry_id = request.form['completed_entry']

    completed_entry = Entry.query.get(completed_entry_id)
    return render_template('completed_entry') 




if __name__ == '__main__':
    app.run()
