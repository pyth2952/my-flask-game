from flask import Flask, render_template, request, redirect, url_for, session, flash
import hashlib
import os

app = Flask(__name__)
app.secret_key = "replace_with_your_secret_key"

USER_FILE = "idpw"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            for line in f:
                if ':' in line:
                    user_id, hashed_pw = line.strip().split(':', 1)
                    users[user_id] = hashed_pw
    return users

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_id = request.form["userid"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        users = load_users()
        if user_id in users:
            flash("이미 존재하는 아이디입니다.")
            return redirect(url_for("register"))

        if password != confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("register"))

        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}:{hash_password(password)}\n")

        flash("회원가입 완료! 로그인 해주세요.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["userid"]
        password = request.form["password"]

        users = load_users()
        hashed_input_pw = hash_password(password)

        if user_id in users and users[user_id] == hashed_input_pw:
            session["user_id"] = user_id
            flash("로그인 성공!")
            return redirect(url_for("home"))
        else:
            flash("아이디 또는 비밀번호가 잘못되었습니다.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", user=session["user_id"])

@app.route("/delete_account", methods=["GET", "POST"])
def delete_account():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        password = request.form["password"]
        user_id = session["user_id"]
        users = load_users()

        if hash_password(password) != users.get(user_id):
            flash("비밀번호가 틀렸습니다.")
            return redirect(url_for("delete_account"))

        users.pop(user_id)

        with open(USER_FILE, "w") as f:
            for uid, pw_hash in users.items():
                f.write(f"{uid}:{pw_hash}\n")

        session.pop("user_id", None)
        flash("회원 탈퇴가 완료되었습니다.")
        return redirect(url_for("login"))

    return render_template("delete_account.html")

@app.route("/game")
def game():
    if "user_id" not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for("login"))
    return render_template("game.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("로그아웃 되었습니다.")
    return redirect(url_for("login"))

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        current_pw = request.form["current_password"]
        new_pw = request.form["new_password"]
        confirm_pw = request.form["confirm_password"]

        users = load_users()
        user_id = session["user_id"]

        if hash_password(current_pw) != users.get(user_id):
            flash("현재 비밀번호가 틀렸습니다.")
            return redirect(url_for("change_password"))

        if new_pw != confirm_pw:
            flash("새 비밀번호가 일치하지 않습니다.")
            return redirect(url_for("change_password"))

        users[user_id] = hash_password(new_pw)
        with open(USER_FILE, "w") as f:
            for uid, pw_hash in users.items():
                f.write(f"{uid}:{pw_hash}\n")

        flash("비밀번호가 성공적으로 변경되었습니다.")
        return redirect(url_for("home"))

    return render_template("change_password.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
