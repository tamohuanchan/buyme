from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import random
import os

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    images = db.Column(db.String(500), nullable=True)  # Здесь должно быть поле для изображений
    published_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата публикации (без ZoneInfo)

    # Внешний ключ, связывающий с User
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



class User(db.Model):
    __tablename__ = 'user'

    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Связь с Position
    positions = db.relationship('Position', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


@app.route("/")  # Главная страница
@app.route("/home")
@app.route('/')
def index():
    positions = Position.query.all()  # Извлекаем все записи из таблицы Position
    return render_template('index.html', positions=positions)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/product/<int:product_id>")
def product(product_id):
    position = Position.query.get_or_404(product_id)  # Получаем товар по ID
    return render_template("product.html", position=position)



@app.route("/registration", methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Проверка совпадения паролей
        if password != confirm_password:
            flash("Пароли не совпадают", category="error")
            return redirect(url_for('registration'))

        # Проверка, существует ли пользователь с таким логином или почтой
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()

        if user_exists:
            flash("Пользователь с таким логином или почтой уже существует.", category="error")
            return redirect(url_for('registration'))

        # Хэширование пароля перед сохранением
        hashed_password = generate_password_hash(password, method='sha256')

        # Создание нового пользователя
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
    if "userLogged" in session:
        username = session["userLogged"]
        return redirect(url_for('profile', username=username))  # Передаем username в URL

    if request.method == "POST":  # Проверка только для POST-запросов
        username = request.form.get('username')
        password = request.form.get('password')

        # Ищем пользователя в базе данных по логину
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):  # Сравниваем хеш пароля
            session["userLogged"] = user.username  # Сохраняем имя пользователя в сессии
            return redirect(url_for('profile', username=user.username))  # Передаем username в URL
        else:
            flash("Неверный логин или пароль!", category='error')  # Сообщение об ошибке

    return render_template("login.html")

@app.route("/profile/<username>")
def profile(username):  # Принимаем username как параметр URL
    if "userLogged" not in session:
        return redirect(url_for('login'))  # Перенаправление на страницу входа, если пользователь не залогинен

    session_username = session["userLogged"]
    if session_username != username:
        return redirect(url_for('login'))  # Если сессия не совпадает с username в URL, редиректим на страницу входа

    return render_template("profile.html", username=username)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("page404.html"), 404


@app.route("/create_position", methods=["POST", "GET"])
def create_position():
    # Проверка, авторизован ли пользователь
    if "userLogged" not in session:
        flash("Вы должны быть авторизованы для добавления товара.", category="error")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        images_data = request.form.get('images', '').strip()
        images = images_data if images_data else None

        id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        # Проверка уникальности ID
        while Position.query.filter_by(id=id_value).first():
            id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        # Получаем имя пользователя из сессии
        username = session["userLogged"]

        # Создаем новый товар
        position = Position(
            id=id_value,
            title=title,
            description=description,
            images=images,
            user_username=username  # Связываем товар с автором
        )

        try:
            db.session.add(position)
            db.session.commit()
            flash("Товар успешно добавлен!", category='success')
            return redirect(url_for('index'))  # Перенаправление на главную страницу
        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка: {str(e)}", category='error')

    return render_template("create_position.html")



if __name__ == "__main__":
    app.run(debug=True)
