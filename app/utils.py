from sqlalchemy.orm import aliased

from app import db
from app.models import Flight, Airport


# def read_flight(diem_di=None, diem_den=None, ngay_di=None):
#     flights = Flight.query
#
#     if diem_di:
#         flights = flights.join(Airport, Flight.departure_airport_id == Airport.id)\
#                             .filter(Airport.address.contains(diem_di)).all()
#
#     if diem_den:
#         flights = flights.filter(Flight.arrival_airport == diem_den)
#
#     if ngay_di:
#         flights = flights.query.filter(Flight.departure_day.contains(ngay_di))
#
#     return flights.all()


