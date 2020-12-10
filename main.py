import uuid
import hashlib
import requests

from flask import Flask, request, make_response, render_template, redirect, url_for
from models import db, User

app = Flask(__name__)
db.create_all()


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")
    if session_token:
        usuario = db.query(User).filter_by(session_token=session_token).first()
    else:
        usuario = None
    return render_template("index.html", user=usuario)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    user = db.query(User).filter_by(email=email).first()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user is None:
        user = User(name=name, email=email, password=hashed_password)

        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    else:
        session_token = str(uuid.uuid4())
        user.session_token = session_token

        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        if user:
            user_name = request.form.get("user-name")
            user_email = request.form.get("user-email")

            user.name = user_name
            user.email = user_email

            db.add(user)
            db.commit()
            return redirect(url_for("profile"))
        else:
            return redirect(url_for("index"))


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        if user:
            user.deleted = True
            db.delete(user)
            db.commit()
            response = make_response(redirect(url_for("index")))
            response.set_cookie("session_token", user=user)
            return response
        else:
            return redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def list_users():
    users = db.query(User).all()
    return render_template("users.html", users=users)


@app.route("/user/<int:user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(user_id)
    return render_template("user_details.html", user=user)


@app.route("/clima", methods=["GET"])
def clima():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Madrid,Es",
        "appid": "ec2d833d7cdcf20d0a03fc26a45658c4",
        "units": "metric"
    }

    response = requests.get(url, params=params)
    return render_template("clima.html", data=response.json())


if __name__ == '__main__':
    app.run(debug=True)
