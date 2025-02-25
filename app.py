from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import random
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Редирект на страницу входа
login_manager.user_loader

@login_manager.user_loader
def load_user(username):
    return User.query.get(username)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.Column(db.String(500), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_username = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    comments = db.relationship('Comment', backref='position', lazy=True)

    def __repr__(self):
        return f"<Position {self.title}>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)

    def __repr__(self):
        return f"<Comment {self.content[:50]}>"

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    positions = db.relationship('Position', backref='user', lazy=True)
    def get_id(self):
        # Возвращаем уникальный идентификатор, например, username
        return self.username
    def __repr__(self):
        return f"<User {self.username}>"



@app.route("/")  # Главная страница
@app.route("/home")
def index():
    positions = Position.query.all()
    return render_template('index.html', positions=positions)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/product/<int:product_id>")
def product(product_id):
    position = Position.query.get_or_404(product_id)
    return render_template("product.html", position=position)

@app.route("/registration", methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Пароли не совпадают", category="error")
            return redirect(url_for('registration'))

        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()

        if user_exists:
            flash("Пользователь с таким логином или почтой уже существует.", category="error")
            return redirect(url_for('registration'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Регистрация прошла успешно! Теперь вы можете войти.", category="success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка при регистрации: {str(e)}", category="error")

    return render_template("registration.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile', username=current_user.username))

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile', username=user.username))
        else:
            flash("Неверный логин или пароль!", category='error')

    return render_template("login.html")

@app.route("/profile/<username>")
@login_required  # Добавим требование авторизации
def profile(username):
    if current_user.username != username:
        return redirect(url_for('login'))

    return render_template("profile.html", username=username)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("page404.html"), 404

@app.route("/create_position", methods=["POST", "GET"])
@login_required  # Добавим требование авторизации
def create_position():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        images_data = request.form.get('images', '').strip()
        images = images_data if images_data else None

        id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        while Position.query.filter_by(id=id_value).first():
            id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        position = Position(id=id_value, title=title, description=description, images=images, user_username=current_user.username)

        try:
            db.session.add(position)
            db.session.commit()
            flash("Товар успешно добавлен!", category='success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка: {str(e)}", category='error')

    return render_template("create_position.html")

if __name__ == "__main__":
    app.run(debug=True)
