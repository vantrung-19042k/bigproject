from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import Integer, String, Column, Float, Date, ForeignKey, Enum, Boolean
from datetime import datetime
from enum import Enum as TypeEnum
from flask_login import UserMixin


# User role
class UserRole(TypeEnum):
    CUSTOMER = 1
    EMPLOYEE = 2
    ADMIN = 3


# model luu tru thong tin user
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    avatar = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)
    joined_date = Column(Date, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.CUSTOMER)

    employee = relationship('Employee', backref='user', lazy=True, uselist=False)

    def __str__(self):
        return self.username


# <---------------------------flight management system------------------------------------>
# management customer
class Customer(db.Model):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    identity_card = Column(String(20), nullable=False)
    address = Column(String(50), nullable=False)

    airticket = relationship('AirTicket', backref='customer', lazy=True)


# management employee
class Employee(db.Model):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    position = Column(String(50), nullable=False)
    phone = Column(String(10), nullable=False)
    address = Column(String(50), nullable=False)

    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    airticket = relationship('AirTicket', backref='employee', lazy=True)


# management flight
class Plane(db.Model):
    __tablename__ = 'plane'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    manufacturer = Column(String(50), nullable=False)

    amount_seat_1 = Column(Integer, nullable=False)
    amount_seat_2 = Column(Integer, nullable=False)
    total_seat = Column(Integer, nullable=False)

    flights = relationship('Flight', backref='plane', lazy=True)

    def __str__(self):
        return str('%s' + 'Mã số: %s', self.name, )


# management airport
class Airport(db.Model):
    __tablename__ = 'airport'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    # acreage = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)

    def __str__(self):
        return self.name


# san bay trung gian
class IntermediateAirport(db.Model):
    __tablename__ = 'intermediate_airport'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)

    flights = relationship('Flight', backref='intermediate_airport', lazy=True)

    def __str__(self):
        return self.name


# management flight
class Flight(db.Model):
    __tablename__ = 'flight'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    departure_day = Column(Date, nullable=False)
    flight_time = Column(String(50), nullable=False)

    plane_id = Column(Integer, ForeignKey(Plane.id), nullable=False)
    departure_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    intermediate_airport_id = Column(Integer, ForeignKey(IntermediateAirport.id), nullable=False)

    departure_airport = relationship('Airport', foreign_keys=[departure_airport_id])
    arrival_airport = relationship('Airport', foreign_keys=[arrival_airport_id])

    air_tickets = relationship('AirTicket', backref='flight', lazy=True)

    def __str__(self):
        return self.name


# management ticket info
class Seat(db.Model):
    __tablename__ = 'seat'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    status = Column(Boolean, nullable=False)


class AirTicket(db.Model):
    __tablename__ = 'airticket'
    id = Column(Integer, ForeignKey(Seat.id), primary_key=True)
    type = Column(String(50), nullable=False)
    price = Column(Float(10), nullable=False)
    date = Column(Date, nullable=False)

    employee_id = Column(Integer, ForeignKey(Employee.id), nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id), nullable=False)


plane_seat = db.Table('plane_seat',
                      Column('plane_id', Integer, ForeignKey(Plane.id), primary_key=True),
                      Column('seat_id', Integer, ForeignKey(Seat.id), primary_key=True)
                      )

if __name__ == "__main__":
    db.create_all()
