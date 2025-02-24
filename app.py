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
            flash("Подтвердите почту для завершения регистрации", category='success')
        else:
            flash('Ошибка', category='error')
        print(request.form)

    return render_template("registration.html")



@app.errorhandler(404)
def pageNotFound(error):
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


