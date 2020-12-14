import hashlib

from flask import render_template, request, redirect
from flask_login import login_user
from sqlalchemy import and_, or_

from app.models import *
from app import app, login, admins, utils
from sqlalchemy.orm import aliased


@app.route('/')
def index():
    return render_template('base/base.html')


@login.user_loader
def user_load(user_id):
    return User.query.get(user_id)


@app.route('/login')
def login():
    return render_template('base/login-cus.html')


@app.route('/register')
def register():
    return render_template('base/registration.html')


# xu ly login
@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password = str(hashlib.md5(
            password.strip().encode("utf-8")).hexdigest())  # băm mật khẩu '202cb962ac59075b964b07152d234b70'
        user = User.query.filter(User.username == username.strip(),
                                 User.password == password.strip()).first()  # .first() nghia là có hoặc không có thì trả về none

        if user:
            login_user(user=user)

    return redirect('/admin')


@app.route('/search-flight')
def search_flight():
    departure_airport = aliased(Airport)
    arrival_airport = aliased(Airport)

    diem_di = request.args.get("diem_di", 0)
    diem_den = request.args.get("diem_den", 0)
    ngay_di = request.args.get("ngay_di", 0)

    # flights = utils.read_flight(ngay_di=ngay_di)

    flights = Flight.query.join(departure_airport, Flight.departure_airport_id == departure_airport.id) \
        .join(arrival_airport, Flight.arrival_airport_id == arrival_airport.id) \
        .filter(and_(departure_airport.address.contains(diem_di), arrival_airport.address.contains(diem_den),
                     Flight.departure_day.contains(ngay_di))).all()

    return render_template('base/search-flight.html', flights=flights)


if __name__ == '__main__':
    app.run(debug=True, port=5055)
