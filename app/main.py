import hashlib

from flask import render_template, request, redirect
from flask_login import login_user

from app.models import *
from app import app, login, admins, utils


@app.route('/')
def index():
    return render_template('base/base.html')


@login.user_loader
def user_load(user_id):
    return User.query.get(user_id)


@app.route('/login-user', methods=['get', 'post'])
def login_users():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '')
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        user = User.query.filter(User.username == username,
                                 User.password == password).first()

        if user:
            login_user(user=user)
            return redirect('/admin')
    elif request.method == 'GET':
        print(request.url)
        return render_template('base/login-cus.html')

    return render_template('base/login-cus.html')


@app.route('/register-user', methods=['get', 'post'])
def register_user():
    err_msg = ''
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if password == confirm_password:
            if utils.add_user(name=name, email=email, username=username,
                              password=password):
                return redirect('/admin')
        else:
            err_msg = "Mật khẩu không khớp, vui lòng thử lại!"
    return render_template('base/registration.html', err_msg=err_msg)


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


# tìm kiềm chuyến bay
@app.route('/search-flight')
def search_flight():
    msg = ''
    flights = None

    diem_di = request.args.get("diem_di", 0)
    diem_den = request.args.get("diem_den", 0)
    ngay_di = request.args.get("ngay_di", 0)

    if diem_di and diem_den and ngay_di:
        flights = utils.read_flight(diem_di=diem_di, diem_den=diem_den, ngay_di=ngay_di)
    else:
        msg = "Vui lòng nhập đầy đủ thông tin"

    return render_template('base/search-flight.html', flights=flights, msg=msg)


if __name__ == '__main__':
    app.run(debug=True, port=5055)
