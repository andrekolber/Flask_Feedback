from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from wtforms.validators import Email
from models import connect_db, db, User, Feedback
from forms import UserSignUpForm, UserLoginForm, UserFeedbackForm


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """redirect user to registration page"""
    if "username" in session:
        return redirect('/users/<username>')
    else:
        return redirect('/login')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Show form to register a new user and handle form submission"""
    form = UserSignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        try:
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            flash("Sign Up Successful!", "success")
            return redirect('/users/<username>')
        except:
            db.session.rollback()
            form.username.errors = ["Username already taken"]

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", 'POST'])
def login_user():
    """Login user and add username to session"""
    form = UserLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            session['username'] = user.username
            flash("Login Successful!", "success")
            return redirect('/users/<username>')
        else:
            form.username.errors = ["Invalid username/password"]

    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user_information(username):
    """Show information about user"""
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        user = User.query.get(session["username"])
        feedbacks = user.feedback
        return render_template('user.html', user=user, feedbacks=feedbacks)

    
@app.route('/logout', methods=["POST"])
def logout_user():
    """Logout user delete username from session"""

    session.pop('username')
    flash("Logged out successfully!", "success")
    return redirect('/login')


@app.route('/users/<username>/delete', methods=["GET", "POST"])
def delete_user(username):
    """Delete a user and remove username from session"""
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect("/login")
    else:
        user = User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("Account deleted", "info")
        return redirect("/register")


@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_user_feedback(username):
    """Display a form for user to add a new feedback"""

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        form = UserFeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            
            flash("Feedback added", "success")
            return redirect('/users/<username>')
    
    
    return render_template('feedback-form.html', form=form)


@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    """Display form to update user feedback and handle form submission"""

    if "username" not in session:
        flash("Please login first!")
        return redirect('/login')
    else:
        user = User.query.get(session["username"])
        feedback = Feedback.query.get(feedback_id)
        form = UserFeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()
            flash("Feedback edited", "info")
            return redirect('/users/<username>')

    return render_template('edit.html', form=form, user=user)


@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete user feedback"""

    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    else:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()

        flash("Feedback Deleted", "info")
        return redirect('/users/<username>')






    
