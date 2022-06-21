from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Note
from forms import RegisterForm, LoginForm, CSRFProtectForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

CURR_USER = "username"


@app.get("/")
def redirect_to_register():
    """ Redirect to register."""

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register_new_user():
    """ Register user: produce form & handle form submission.

    """

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(name, pwd, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()

        session[CURR_USER] = new_user.username

        # on successful login, redirect to users/<username> page
        return redirect(f"/users/{new_user.username}")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Produce login form or handle login.

    """

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session[CURR_USER] = user.username
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)



@app.get('/users/<username>')
def show_user_page(username):
    """authenticate if logged in and shows user information.
    redirects to register page if not logged in
    """
    if username != session.get(CURR_USER):
        flash("You must be logged in to view!")
        return redirect("/")

    user = User.query.get_or_404(username)
    form = CSRFProtectForm()

    notes = Note.query.filter(Note.owner == username).all()

    return render_template("user.html", user=user, form=form, notes=notes)

@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage/register page."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
        flash("Log out successful")
        session.pop(CURR_USER, None)


    return redirect("/")

@app.post("/users/<username>/delete")
def delete_user_and_notes(username):
    """Deletes the user instance and their associated notes"""

    if username != session.get(CURR_USER):
        flash("You must be logged in to view!")
        return redirect("/")

    user = User.query.get_or_404(username)
    notes = Note.query.filter(Note.owner == username).all()

    for note in notes:
        db.session.delete(note)

    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} deleted.")

    return redirect("/")

@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def add_new_user_note(username):
    """display new note form and handle submission"""

    form = NewNoteForm()

    if form.validate_on_submit():
        new_note = Note(
            title=form.title.data,
            content=form.content.data,
            owner=username
            )
        db.session.add(new_note)
        db.session.commit()
        flash(f"Note '{new_note.title}' added.")
        return redirect(f'/users/{username}')
    else:
        return render_template("new_note.html", form=form)