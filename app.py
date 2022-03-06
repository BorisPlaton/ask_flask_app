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

    db = get_db()
    cur = db.execute("""
                SELECT asker.user_name AS asker_name, expert.user_name AS expert_name, question.id AS id, question.text_question as text 
                FROM question 
                    JOIN user AS asker ON question.id_user = asker.id
                    JOIN user AS expert ON question.id_expert = expert.id
                WHERE question.answer IS NOT NULL;
            """)
    questions = cur.fetchall()

    return render_template("home.html", user=user, questions=questions)


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
        if check_password_hash(cur.fetchone()["password"], request.form["password"]):   # Сравниваем хэш паролей
            session["user"] = user_name
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/ask_a_question", methods=["POST", "GET"])
def ask_question():
    user = user_session()

    if not user:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.execute("""
        SELECT * FROM user
        WHERE expert = 1;
    """)
    experts = cur.fetchall()

    if request.method == "POST":
        db.execute("""
            INSERT INTO question (id_expert, id_user, text_question)
            VALUES
                (?, ?, ?);
        """, [request.form["expert_id"], user["id"], request.form["question_text"]])
        db.commit()
        return redirect(url_for("ask_question"))

    return render_template("ask_question.html", user=user, experts=experts)


@app.route("/answer_a_question/<id_question>", methods=["POST", "GET"])
def answer_question(id_question):
    user = user_session()

    if not user:    # Если пользователь в сессии
        return redirect(url_for("login"))

    if user["expert"]:  # Есть ли права эксперта
        if request.method == "POST":
            db = get_db()
            db.execute("""
                UPDATE question
                SET answer = (?)
                WHERE id = (?);
            """, [request.form["answer"], id_question])
            db.commit()
            return redirect(url_for("answer_question", id_question=id_question))
        return render_template("answer_question.html", user=user, id_question=id_question)

    return redirect(url_for("home"))


@app.route("/unanswered_questions")
def unanswered_question():
    user = user_session()

    if not user:    # Если пользователь в сессии
        return redirect(url_for("login"))

    if user["expert"]:  # Есть ли права эксперта
        db = get_db()
        cur = db.execute("""
            SELECT * FROM 
                question JOIN user ON question.id_user = user.id
            WHERE question.id_expert = (?) and question.answer IS NULL;
        """, [user["id"]])
        questions = cur.fetchall()
        return render_template("unaswered_question.html", user=user, questions=questions)
    else:
        return redirect(url_for("home"))


@app.route("/answered_questions/<id_question>")
def answered_questions(id_question):
    user = user_session()

    db = get_db()
    cur = db.execute("""
                    SELECT asker.user_name AS asker_name, expert.user_name AS expert_name, question.id AS id, question.text_question as text, question.answer as answer
                    FROM question 
                        JOIN user AS asker ON question.id_user = asker.id
                        JOIN user AS expert ON question.id_expert = expert.id
                    WHERE question.answer IS NOT NULL and question.id = (?);
                """, [id_question])
    question = cur.fetchone()

    if question:
        return render_template("answered_question.html", user=user, question=question)

    return redirect(url_for("home"))


@app.route("/users")
def users():
    user = user_session()

    if not user:    # Если пользователь в сессии
        return redirect(url_for("login"))

    if user["admin"]:  # Есть ли права админа
        db = get_db()
        cur = db.execute("""
            SELECT * FROM user;
        """)
        users_lists = cur.fetchall()
        return render_template("users.html", user=user, users_list=users_lists)
    else:
        return redirect(url_for("home"))


@app.route("/promote/<user_id>/<role>")
def promote(user_id, role):
    user = user_session()

    if not user:  # Если пользователь в сессии
        return redirect(url_for("login"))

    if user["admin"]:  # Есть ли права админа
        db = get_db()
        if role == 'admin':
            db.execute("""
                UPDATE user 
                SET admin = CASE WHEN admin=1 THEN 0 ELSE 1 END
                WHERE id = (?);
            """, [user_id])
            db.commit()
        elif role == "expert":
            db.execute("""
                UPDATE user 
                SET expert = CASE WHEN expert=1 THEN 0 ELSE 1 END
                WHERE id = (?);
            """, [user_id])
            db.commit()
        return redirect(url_for("users"))
    else:
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
