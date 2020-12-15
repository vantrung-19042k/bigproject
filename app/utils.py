import hashlib

from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_

from app import db
from app.models import User, Flight, Airport


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


