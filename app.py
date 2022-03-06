from flask import Flask, render_template, g, session, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)


def user_session():
    """Возвращает данные пользователя, если тот зашёл в свой аккаунт"""
    user_data = None
    if "user" in session:
        db = get_db()
        cur = db.execute("""
            SELECT * FROM user
            WHERE user_name = (?);
        """, [session["user"]])
        user_data = cur.fetchone()
    return user_data


def connect_db():  # Подключение базы данных
    sql = sqlite3.connect("ask_db.db")
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
    user = user_session()
    return render_template("home.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":  # Если пользователь регистрируется
        db = get_db()
        user_name = request.form["login"]
        password = generate_password_hash(request.form["password"], method="sha256")  # Хэшируем пароль пользователя
        db.execute("""
            INSERT INTO user (user_name, password, expert, admin)
            VALUES
                (?, ?, ?, ?);
        """, [user_name, password, False, False])
        db.commit()
        session["user"] = user_name
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":    # Если пользователь входит
        db = get_db()
        user_name = request.form["login"]
        cur = db.execute("""
            SELECT password FROM user
            WHERE user_name = (?);
        """, [user_name])
        if check_password_hash(cur.fetchone()["password"], request.form["password"]):
            session["user"] = user_name
            return redirect(url_for("home"))

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
