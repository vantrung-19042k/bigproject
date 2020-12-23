import hashlib

from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, extract, func
from sqlalchemy.orm.attributes import Event

from app import db
from app.models import *


def add_user(name, email, username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(name=name,
             email=email,
             username=username,
             password=password)
    try:
        db.session.add(u)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


def read_flight(diem_di=None, diem_den=None, ngay_di=None):
    departure_airport = aliased(Airport)
    arrival_airport = aliased(Airport)

    flights = Flight.query.join(departure_airport, Flight.departure_airport_id == departure_airport.id) \
        .join(arrival_airport, Flight.arrival_airport_id == arrival_airport.id) \
        .filter(and_(departure_airport.address.contains(diem_di), arrival_airport.address.contains(diem_den),
                     Flight.departure_day.contains(ngay_di))).all()

    return flights


def read_data_flight_by_id(id_flight):
    flights = Flight.query.get(id_flight)

    return flights


def add_customer_info(name=None, phone=None, identity_card=None, address=None):
    customer = Customer(name=name, phone=phone, identity_card=identity_card, address=address)

    try:
        db.session.add(customer)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


def read_data_customer_by_phone(phone):
    customer = Customer.query.filter_by(phone=phone).first()

    return customer


# thêm thông tin vé
def add_book_ticket_info(type=None, price=None, customer_id=None, flight_id=None):
    book_ticket = BookTicket(type=type, price=price, customer_id=customer_id, flight_id=flight_id)

    try:
        db.session.add(book_ticket)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


# đọc dữ liệu phiếu đặt chỗ
def read_data_book_ticket():
    departure_airport = aliased(Airport)
    arrival_airport = aliased(Airport)

    book_tickets = BookTicket.query.join(Flight, BookTicket.flight_id == Flight.id) \
        .join(Customer, BookTicket.customer_id == Customer.id) \
        .add_columns(Flight.id.label('id_flight'),
                     Flight.departure_day, Flight.flight_time,
                     Customer.name, Customer.phone,
                     BookTicket.type, BookTicket.price, BookTicket.id.label('id_book_ticket'),
                     BookTicket.status) \
        .all()

    return book_tickets


# đọc dữ liệu phiếu đặt chỗ bằng id
def read_data_book_ticket_by_id(id_book_ticket):
    data_book_ticket = BookTicket.query.filter_by(id=id_book_ticket).first()

    return data_book_ticket


# thêm thông tin vé
def add_ticket(type=None, price=None, date=None, seat_id=None,
               employee_id=None, customer_id=None, flight_id=None):
    air_ticket = AirTicket(type=type, price=price, date=date, seat_id=seat_id,
                           employee_id=employee_id, customer_id=customer_id, flight_id=flight_id)

    try:
        db.session.add(air_ticket)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


# lấy dữ liệu ghế ngồi
def read_data_seat(plane_id):
    data_seat = Seat.query.filter(Seat.plane_id.contains(plane_id)).all()
    return data_seat


# cập nhật trạng thái ghế ngồi
def update_data_seat(seat_id):
    seat = Seat.query.get(seat_id)

    seat.status = True

    try:
        db.session.add(seat)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


# cập nhật trạng thái phiếu đặt chỗ
def update_data_book_ticket(book_ticket_id):
    book_ticket = BookTicket.query.get(book_ticket_id)

    book_ticket.status = 1

    try:
        db.session.add(book_ticket)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


# lấy dữ liệu báo cáo tháng
def read_data_report_month(month):
    report_month = AirTicket.query.join(Flight, AirTicket.flight_id == Flight.id) \
        .filter(extract('month', AirTicket.date) == month) \
        .add_columns(func.count(AirTicket.id).label('SoVe'),
                     func.sum(AirTicket.price).label('DoanhThu'),
                     Flight.id,
                     Flight.name,
                     Flight.flight_time,
                     Flight.departure_day) \
        .group_by(Flight.id) \
        .all()

    return report_month


# lấy dữ liệu báo cáo năm
def read_data_report_year(year):
    report_year = AirTicket.query.join(Flight, AirTicket.flight_id == Flight.id) \
        .filter(extract('year', AirTicket.date) == year) \
        .add_columns(func.count(AirTicket.id).label('SoChuyenBay'),
                     func.sum(AirTicket.price).label('DoanhThu'),
                     (extract('month', AirTicket.date)).label('thang')) \
        .group_by(extract('month', AirTicket.date)) \
        .all()
    return report_year
