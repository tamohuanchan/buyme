from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import random
import os

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

class Positions(db.Model):
    id = db.Column(db.String(9), primary_key=True)  # ID состоит из 9 символов
    title = db.Column(db.String(255), nullable=False)  # Название товара
    description = db.Column(db.Text, nullable=False)  # Описание товара
    characteristics = db.Column(db.JSON, nullable=True)  # Характеристики в формате JSON
    images = db.Column(db.Text, nullable=True)  # Изображения товара (строка)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата публикации

    def __repr__(self):
        return f"<Positions {self.id}>"

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
        nickname = request.form.get('nickname')
        if nickname and len(nickname) > 2:
            flash("Подтвердите почту для завершения регистрации")
        else:
            flash('Ошибка')
        print(request.form)

    return render_template("registration.html")

@app.route("/feed")
def feed():
    positions = Positions.query.order_by(Positions.published_at.desc()).all()

    return render_template("feed.html", positions=positions)

@app.route("/feed/<string:id>")
def position(id):
    position = Positions.query.get(id)
    return render_template("position.html", position=position)

@app.route("/feed/<string:id>/delete")
def position_delete(id):
    position = Positions.query.get_or_404(id)
    try:
        db.session.delete(position)
        db.session.commit()
        return redirect('/feed')
    except Exception as e:
        return f"Произошла ошибка: {e}"


@app.route("/feed/<string:id>/update", methods=["POST", "GET"])
def position_update(id):
    position = Positions.query.get_or_404(id)  # Получаем объект из БД или 404

    if request.method == "POST":
        position.title = request.form['title']
        position.description = request.form['description']
        images_data = request.form.get('images', '').strip()
        position.images = images_data if images_data else None  # Обновляем изображения

        try:
            db.session.commit()  # Фиксируем изменения
            return redirect('/feed')
        except Exception as e:
            return f"Произошла ошибка: {e}"

    return render_template("position_update.html", position=position)


@app.route("/create_position", methods=["POST", "GET"])
def create_position():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        images_data = request.form.get('images', '').strip()
        images = images_data if images_data else None

        id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))

        # Проверка уникальности ID
        while Positions.query.filter_by(id=id_value).first():
            id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))
        position = Positions(id=id_value, title=title, description=description, images=images)
        try:
            db.session.add(position)
            db.session.commit()
            return redirect('/feed')
        except Exception as e:
            db.session.rollback()
            return f"Произошла ошибка: {str(e)}"

    return render_template("create_position.html")

if __name__ == "__main__":
    app.run(debug=True)


