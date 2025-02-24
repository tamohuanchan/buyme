from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)


class Position(db.Model):
    id = db.Column(db.String(9), primary_key=True)  # ID состоит из 9 символов
    title = db.Column(db.String(255), nullable=False)  # Название товара
    description = db.Column(db.Text, nullable=False)  # Описание товара
    characteristics = db.Column(db.JSON, nullable=True)  # Характеристики в формате JSON
    images = db.Column(db.Text, nullable=True)  # Изображения товара (строка)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата публикации

    def __repr__(self):
        return f"<Position {self.id}>"


@app.route("/")  # Главная страница
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/registration", methods=["POST", "GET"])
def registration():
    if request.method == "POST":
        username = request.form.get('username')
        if username and len(username) > 2:
            flash("Подтвердите почту для завершения регистрации", category='success')
        else:
            flash('Ошибка', category='error')

    return render_template("registration.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if "userLogged" in session:
        username = session["userLogged"]
        return redirect(url_for('profile', username=username))  # Передаем username в URL

    if request.method == "POST":  # Проверка только для POST-запросов
        username = request.form.get('username')
        password = request.form.get('password')

        # Простой пример проверки логина и пароля
        if username == 'test' and password == '123':
            session["userLogged"] = username  # Сохраняем имя пользователя в сессии
            return redirect(url_for('profile', username=username))  # Передаем username в URL
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
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        images_data = request.form.get('images', '').strip()
        images = images_data if images_data else None

        id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        # Проверка уникальности ID
        while Position.query.filter_by(id=id_value).first():
            id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        position = Position(id=id_value, title=title, description=description, images=images)
        try:
            db.session.add(position)
            db.session.commit()
            flash("Товар успешно добавлен!", category='success')
            return redirect(url_for('index'))  # Используем url_for для гибкости
        except Exception as e:
            db.session.rollback()
            flash(f"Произошла ошибка: {str(e)}", category='error')

    return render_template("create_position.html")


if __name__ == "__main__":
    app.run(debug=True)


