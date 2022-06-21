from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User
from forms import RegisterForm, LoginForm, CSRFProtectForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()



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

        session["username"] = new_user.username

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
            session["username"] = user.username
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)



@app.get('/users/<username>')
def show_user_page(username):
    """authenticate if logged in and shows user information.
    redirects to register page if not logged in
    """
    user = User.query.get_or_404(username)
    form = CSRFProtectForm()

    if not user.username == session.get("username"):
        flash("You must be logged in to view!")
        return redirect("/")
    else:
        return render_template("user.html", user=user, form=form)

@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage/register page."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
        flash("Log out successful")
        session.pop("username", None)


    return redirect("/")