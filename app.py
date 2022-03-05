from flask import Flask, render_template

app = Flask(__name__)


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
