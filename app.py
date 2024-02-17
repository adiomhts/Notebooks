from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ProfileForm, RegisterForm
  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'esfjEJfjeisd84us8HIHIg379ji' 
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(401)
def unauthorized(error):
    return render_template('login.html', error="You have to sign in to continue."), 401


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    notes = db.relationship('Note', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    try:
        if current_user.is_authenticated:
            notes = Note.query.filter_by(user_id=current_user.id).all()
            return render_template('index.html', notes=notes)
        else:
            return redirect(url_for('login'))
    except:
        return redirect(url_for('error'))


@app.route('/error')
def error():
    try:
        return render_template('error.html')
    except:
        return "Error"


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegisterForm()

        if request.method != 'POST':
            return render_template('register.html', form=form)
        
        
        if not form.validate_on_submit():
            return render_template('register.html', form=form)
        
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            error = 'This e-mail adress is already used.'
            return render_template('register.html', form=form, error=error)
        
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            error = "This username is already used."
            return render_template('register.html', form=form, error=error)
        
        new_user = User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
        
    except:
        return redirect(url_for('error'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method != 'POST':
            return render_template('login.html')

        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = "Wrong password or username. Please, try again."
            return render_template('login.html', error=error)
        
    except:
        return redirect(url_for('error'))


@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('home'))
    except:
        return redirect(url_for('error'))


@app.route('/note', methods=['POST'])
@login_required
def add_note():
    try:
        title = request.form.get('title')
        content = request.form.get('content')
        note = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('home'))
    except:
        return redirect(url_for('error'))


@app.route('/note/<int:id>')
@login_required
def view_note(id):
    try:
        note = Note.query.get(id)
        return render_template('note.html', note=note)
    except:
        return redirect(url_for('error'))
    

@app.route('/note/<int:id>/edit', methods=['POST'])
@login_required
def edit_note(id):
    try:
        note = Note.query.get(id)
        note.title = request.form.get('title')
        note.content = request.form.get('content')
        db.session.commit()
        return redirect(url_for('home'))
    except:
        return redirect(url_for('error'))
    

@app.route('/note/<int:id>/delete', methods=['POST'])
@login_required
def delete_note(id):
    try:
        note = Note.query.get(id)
        db.session.delete(note)
        db.session.commit()
        return redirect(url_for('home'))
    except:
        return redirect(url_for('error'))
    

@app.route('/profile')
@login_required
def profile():
    try:    
        return render_template('profile.html', user=current_user)
    except:
        return redirect(url_for('error'))
    

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    try:
        form = ProfileForm()

        if not form.validate_on_submit():
            return render_template('edit_profile.html', form=form)
        
        if form.old_password.data and not check_password_hash(current_user.password_hash, form.old_password.data):
            error = 'Wrong password.'
            return render_template('edit_profile.html', form=form, error=error)
        
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data

        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            error = 'New e-mail adress is already used.'
            return render_template('edit_profile.html',form=form, error=error)
        
        current_user.email = form.email.data

        if form.new_password.data and form.new_password.data == form.confirm_password.data:
            current_user.set_password(form.new_password.data)
        

        db.session.commit()
        return redirect(url_for('profile'))
    except:
        return redirect(url_for('error')) 



if __name__ == '__main__':
        app.run(debug=True)
