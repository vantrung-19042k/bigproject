import hashlib

from flask import render_template, request, redirect, g
from flask_login import login_user, current_user

from app.models import *
from app import app, login, admins, utils, decorator
from datetime import date


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


@app.route('/book-tickets', methods=['get', 'post'])
def book_tickets():
    id_flight = None
    flights = None

    if request.method == 'POST':
        id_flight = request.form.get('btn-chon')
        flights = utils.read_data_flight_by_id(id_flight=id_flight)

    return render_template('base/book-tickets.html', flights=flights)


@app.route('/book-tickets-result', methods=['post', 'get'])
def book_tickets_result():
    wait_time = 1000
    seconds = wait_time / 1000
    redirect_url = '/'

    id_flight = None
    name = None
    phone = None
    cmnd = None
    dia_chi = None
    loai_ve = None

    msg = ''

    if request.method == 'POST':
        id_flight = request.form.get('btn-xacnhan')
        name = request.form.get('name')
        phone = request.form.get('phone')
        identity_card = request.form.get('cmnd')
        address = request.form.get('dia_chi')
        type = request.form.get('loai_ve')

        if utils.add_customer_info(name=name, phone=phone, identity_card=identity_card, address=address):
            customer = utils.read_data_customer_by_phone(phone=phone)
            flight = utils.read_data_flight_by_id(id_flight=id_flight)

            if utils.add_book_ticket_info(type=type, price=flight.price, customer_id=customer.id, flight_id=flight.id):
                # return render_template('base/book-tickets-result.html', msg='Đặt vé thành công')
                return f"<html><body><h1>Đặt vé thành công, chuyển hướng sau {seconds} seconds</h1>" \
                       f"<script>var timer = setTimeout(function() {{window.location='{redirect_url}'}}, " \
                       f"{wait_time});</script></body></html>"
            else:
                # return render_template('base/book-tickets-result.html', msg='Đặt vé thất bại')
                return f"<html><body><h1>Đặt vé thất bại, chuyển hướng sau {seconds} seconds</h1>" \
                       f"<script>var timer = setTimeout(function() {{window.location='{redirect_url}'}}, " \
                       f"{wait_time});</script></body></html>"

    return render_template('base/book-tickets-result.html')


@app.route('/confirm-ticket', methods=['get', 'post'])
def confirm_ticket():
    wait_time = 1000
    seconds = wait_time / 1000
    redirect_url = '/admin/confirmticket/'

    msg = ''

    id_book_ticket = None

    ticket_type = None
    price = None
    ticket_date = None
    customer_id = None
    employee_id = None
    flight_id = None
    seat_id = None

    seat_data = None

    book_ticket = utils.read_data_book_ticket()

    if request.method == 'POST':
        id_book_ticket = request.form.get('btn-confirm-ticket')

        data_book_ticket = utils.read_data_book_ticket_by_id(id_book_ticket=id_book_ticket)

        ticket_type = data_book_ticket.type
        price = data_book_ticket.price
        ticket_date = date.today()
        customer_id = data_book_ticket.customer_id
        employee_id = current_user.get_id()
        flight_id = data_book_ticket.flight_id

        # xếp vào một ghế ngẫu nhiên
        # seat_id = data_book_ticket.id

        data_flight = utils.read_data_flight_by_id(flight_id)
        plane_id = data_flight.plane_id

        data_seat = utils.read_data_seat(plane_id)

        for s in data_seat:
            if not s.status:
                seat_id = s.id
                break

        if utils.add_ticket(type=ticket_type, price=price, date=ticket_date,
                            customer_id=customer_id, employee_id=employee_id, flight_id=flight_id,
                            seat_id=seat_id):
            utils.update_data_seat(seat_id)
            utils.update_data_book_ticket(book_ticket_id=id_book_ticket)
            # return render_template('base/confirm-tickets-result.html', msg='Xác nhận đặt vé thành công')
            return f"<html><body><h1>Xác nhận đặt vé thành công, chuyển hướng sau {seconds} seconds</h1>" \
                   f"<script>var timer = setTimeout(function() {{window.location='{redirect_url}'}}, " \
                   f"{wait_time});</script></body></html>"
        else:
            # return render_template('base/confirm-tickets-result.html', msg='Xác nhận đặt vé thất bại')
            return f"<html><body><h1>Xác nhận đặt vé thất bại, chuyển hướng sau {seconds} seconds</h1>" \
               f"<script>var timer = setTimeout(function() {{window.location='{redirect_url}'}}, " \
               f"{wait_time});</script></body></html>"

        # if current_user.is_authenticated:
        #     user_id = current_user.get_id()``
        #     print(user_id)
        #     today = date.today()
        #     print(today)

    return render_template('base/confirm-tickets.html', book_ticket=book_ticket)


# @app.route('/report-month')
# def report_month():
#
#     report_month = utils.read_data_report_month()
#
#     return render_template('base/report-month.html', report_month=report_month)
#
#
# @app.route('/report-year')
# def report_year():
#
#     report_year = utils.read_data_report_year()
#
#     return render_template('base/report-year.html', report_year=report_year)


if __name__ == '__main__':
    app.run(debug=True, port=5055)
