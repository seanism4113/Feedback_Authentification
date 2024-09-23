from flask import Flask, render_template, session, flash, redirect, url_for
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.app_context().push()

app.config['SECRET_KEY'] = 'dragons145'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_feedback_db'

connect_db(app)
db.create_all()

def is_logged_in():
    return 'username' in session

@app.route('/')
def home_redirect():
    """ Redirect homepage of site to registration page"""
    return redirect(url_for('register_user'))


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """ Displays registration form and handles submission"""

    if is_logged_in():
        return redirect(url_for('show_user_information', username=session['username']))
    
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User.register(username = form.username.data,
                        password = form.password.data,
                        email = form.email.data,
                        first_name = form.first_name.data,
                        last_name = form.last_name.data)
        
        db.session.add(new_user)
        try:
            db.session.commit()
            session['username'] = new_user.username
            flash('Successfully Registered!', 'success')
            return redirect(url_for('show_user_information', username = new_user.username))
        except IntegrityError:
            db.session.rollback()
            form.username.errors.append('Username is taken. Please select another')

    return render_template('/users/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ Render Form and Login User """

    if is_logged_in():
        return redirect(url_for('show_user_information', username=session['username']))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            session['username'] = user.username
            flash('Welcome back', 'info')
            return redirect(url_for('show_user_information', username = user.username))
        form.password.errors.append('Invalid username or password')
        
    return render_template('/users/login.html', form = form)


@app.route('/users/<username>')
def show_user_information(username):
    """ Display information about the user as well as Feedback"""
    if not is_logged_in() or username != session['username']:
        flash('Unauthorized to view this page', 'danger')
        return redirect(url_for('login_user'))

    user = User.query.filter_by(username=username).first_or_404()
    feedback = Feedback.query.filter_by(username = user.username).order_by(Feedback.id.desc()).all()
    return render_template('/users/user-details.html', user = user, feedback = feedback)


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """ Delete user as well as any associated feedback"""
    if not is_logged_in() or username != session['username']:
        flash('Unauthorized to view this page', 'danger')
        return redirect(url_for('login_user'))
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username', None)
    flash('Account has been deleted', 'danger')
    return redirect(url_for('login_user'))


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """ Show Feedback form and submit new Feedback entry"""
    if not is_logged_in or username != session['username']:
        flash('Unauthorized to view this page', 'danger')
        return redirect(url_for('login_user'))
    
    form = FeedbackForm()

    if form.validate_on_submit():
        new_feedback = Feedback(title = form.title.data, content = form.content.data, username = username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback added!', 'success')
        return redirect(url_for('show_user_information', username = username))
    
    return render_template('/feedback/feedback.html', form = form)


@app.route('/feedback/<int:id>/update', methods=['GET','POST'])
def update_feedback(id):
    """ Show Feedback form with current data and update form"""
    feedback = Feedback.query.get_or_404(id)

    if not is_logged_in() or feedback.username != session['username']:
        flash('Unauthorized to view this page', 'danger')
        return redirect(url_for('login_user'))
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash('Feedback updated!', 'success')
        return redirect(url_for('show_user_information', username=session['username']))
    
    return render_template('/feedback/feedback.html', form = form)

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    """ Delete a feedback Post"""
    feedback = Feedback.query.get_or_404(id)

    if not is_logged_in() or feedback.username != session['username']:
        flash('Unauthorized to view this page', 'danger')
        return redirect(url_for('login_user'))

    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted', 'warning')
    return redirect(url_for('show_user_information', username=session['username']))

@app.route('/logout')
def logout_user():
    """ Logout a user """
    session.pop('username', None)
    flash('Goodbye', 'secondary')
    return redirect(url_for('login_user'))