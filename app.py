from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import  SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import random




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:pass@192.168.0.139:5434/buyme"
db = SQLAlchemy(app)

from datetime import datetime

class Positions(db.Model):
    id = db.Column(db.String(9), primary_key=True)  # ID состоит из 9 символов
    title = db.Column(db.String(255), nullable=False)  # Название товара
    description = db.Column(db.Text, nullable=False)  # Описание товара
    characteristics = db.Column(db.JSON, nullable=True)  # Характеристики в формате JSON
    images = db.Column(db.Text, nullable=True)  # Изображения товара (строка)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата публикации (без ZoneInfo)


    def __repr__(self):
        return "<Positions %r>" % self.id


@app.route("/")  # главная стр
@app.route("/home")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

# @app.route("/user/<string:user_name>")
# def user(user_name):
#     return render_template("user.html")

@app.route("/create_position", methods=["POST", "GET"])
def create_position():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']

        images_data = request.form.get('images', '').strip()  # Получаем строку, убираем лишние пробелы
        images = images_data if images_data else None  # Оставляем строку без парсинга в JSON

        id_value = ''.join(str(random.randint(0, 9)) for _ in range(9))  # Генерируем 9-значный ID

        position = Positions(id=id_value, title=title, description=description, images=images)
        try:
            db.session.add(position)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"Произошла ошибка: {e}"

    return render_template("create_position.html")

if __name__ == "__main__":
    app.run(debug=True)
