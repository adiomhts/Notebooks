from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ProfileForm


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'esfjEJfjeisd84us8HIHIg379ji' 
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

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
    if current_user.is_authenticated:
        notes = Note.query.filter_by(user_id=current_user.id).all()
        return render_template('index.html', notes=notes)
    else:
        return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user = User.query.filter_by(username=username).first()
        
        # Проверяем, существует ли уже пользователь с таким адресом электронной почты
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = 'Адрес электронной почты уже занят'
            return render_template('register.html', error=error)
        
        if user is None:
            new_user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
        else:
            error = "Пользователь с таким именем уже существует."
            return render_template('register.html', error=error)
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = "Неправильный логин или пароль. Пожалуйста, попробуйте снова."
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/note', methods=['POST'])
@login_required
def add_note():
    title = request.form.get('title')
    content = request.form.get('content')
    note = Note(title=title, content=content, user_id=current_user.id)
    db.session.add(note)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/note/<int:id>')
@login_required
def view_note(id):
    note = Note.query.get(id)
    return render_template('note.html', note=note)

@app.route('/note/<int:id>/edit', methods=['POST'])
@login_required
def edit_note(id):
    note = Note.query.get(id)
    note.title = request.form.get('title')
    note.content = request.form.get('content')
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/note/<int:id>/delete', methods=['POST'])
@login_required
def delete_note(id):
    note = Note.query.get(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        return redirect(url_for('profile'))  # Перенаправление на страницу профиля после успешного обновления
    return render_template('edit_profile.html', form=form)





if __name__ == '__main__':
        app.run(debug=True)
