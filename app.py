from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)


def connect_db():  # Подключение базы данных
    sql = sqlite3.connect("food.db")
    sql.row_factory = sqlite3.Row
    return sql


def get_db():  # Получение базы данных
    if not hasattr(g, "sqlite3"):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):  # Закрытие соединения с базой данных при получении страницы
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/ask_a_question")
def ask_question():
    return render_template("ask_question.html")


@app.route("/answer_a_question")
def answer_question():
    return render_template("answer_question.html")


@app.route("/unanswered_questions")
def unanswered_question():
    return render_template("unaswered_question.html")


@app.route("/answered_questions")
def answered_questions():
    return render_template("answered_question.html")


@app.route("/users")
def users():
    return render_template("users.html")


if __name__ == "__main__":
    app.run(debug=True)
