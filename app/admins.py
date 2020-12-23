from datetime import date

from app import db, admin, utils

from flask import request, render_template
from flask_login import current_user, logout_user
from werkzeug.utils import redirect
from wtforms import PasswordField, validators

from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose

from app.models import *


class UserView(ModelView):
    can_edit = True
    can_create = True
    can_export = True
    can_delete = False
    column_display_pk = True
    # form_extra_fields = {
    #     "password": PasswordField("Password", validators=[validators.data_required(),
    #                                                       validators.length(min=8, max=100)])}

    def is_accessible(self):
        return current_user.is_authenticated


class SubModelView(ModelView):
    can_export = True
    can_edit = True
    can_delete = True
    column_display_pk = True

    # kiem tra trang thai dang nhap cua user
    # neu đã đăng nhập mới hiển thị các view

    def is_accessible(self):
        return current_user.is_authenticated


class ReportView(ModelView):
    can_export = True
    can_edit = True
    can_delete = True
    column_display_pk = True

    # def is_accessible(self):
    #     return current_user.is_authenticated


# class ReportMonthView(ReportView):
#     column_labels = dict(flight='Chuyến bay', total_ticket='Tổng số vé', sales='Doanh thu',
#                          employee='Nhân viên')
#
#
# class ReportYearView(ReportView):
#     column_labels = dict(month='Tháng', total_flight='Tổng chuyến bay', sales='Doanh thu',
#                          employee='Nhân viên')


class CustomerView(SubModelView):
    column_labels = dict(name='Tên', phone='SĐT', identity_card='CMND', address='Địa chỉ',
                         airticket='Vé bán', bookticket='Phiếu đặt chỗ')


class EmployeeView(SubModelView):
    column_labels = dict(name='Tên', position='Chức vụ', phone='SĐT', address='Địa chỉ',
                         airticket='Vé bán', report_month='Báo cáo tháng', report_year='Báo cáo năm')


class AirportView(SubModelView):
    column_labels = dict(name='Tên', address='Địa chỉ', acreage='Diện tích', status='Trạng thái')


class IntermediateAirportView(SubModelView):
    column_labels = dict(name='Tên', address='Địa chỉ', acreage='Diện tích', status='Trạng thái', flights='Chuyến bay')


class PlaneView(SubModelView):
    column_labels = dict(name='Tên', manufacturer='Hãng sản xuất', size='Kích thước',
                         amount_seat_1='Số ghế phổ thông (1)', amount_seat_2='Số ghế thương gia (2)',
                         total_seat='Tổng số ghế', flights='Chuyến bay', seats='Ghế')


class FlightView(SubModelView):
    column_labels = dict(name='Tên', departure_day='Ngày đi', arrival_day='Ngày đến',
                         flight_time='Thời gian bay', price='Giá', departure_airport='Sân bay đi',
                         arrival_airport='Sân bay đến', plane='Máy bay', air_tickets='Vé bán',
                         book_tickets='Phiếu đặt chỗ', intermediate_airport='Sân bay trung gian')


class TicketView(SubModelView):
    column_labels = dict(type='Loại vé', price='Giá bán', date='Ngày xuất vé', flight='Chuyến bay',
                         customer='Khách hàng', employee='Nhân viên', seat='Ghế')


class BookTicketView(SubModelView):
    column_labels = dict(type='Loại vé', price='Giá bán', flight='Chuyến bay',
                         customer='Khách hàng', status='Trạng thái')


class SeatView(SubModelView):
    column_labels = dict(name='Tên ghế', status='Trạng thái',
                         air_ticket='Vé bán', plane='Máy bay')


# tao view rieng khong lien quan cac model
class Contact(BaseView):
    @expose('/')
    def contact(self):
        return self.render('admin/contact.html')

    # kiem tra trang thai dang nhap cua user
    # neu đã đăng nhập mới hiển thị các view
    def is_accessible(self):
        return current_user.is_authenticated


class ConfirmTicket(BaseView):
    @expose('/')
    def confirm_ticket(self):
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
                return f"<html><body><h1>Xác nhận đặt vé thành công, chuyển hướng sau {seconds} seconds</h1>" \
                       f"<script>var timer = setTimeout(function() {{window.location='{redirect_url}'}}, " \
                       f"{wait_time});</script></body></html>"
            else:
                return f"<html><body><h1>Xác nhận đặt vé thất bại, chuyển hướng sau {seconds} seconds</h1>" \
                       f"<script>var timer = setTimeout(function() {{window.location='{redirect_url}'}}, " \
                       f"{wait_time});</script></body></html>"

            # if current_user.is_authenticated:
            #     user_id = current_user.get_id()``
            #     print(user_id)
            #     today = date.today()
            #     print(today)

        return self.render('base/confirm-tickets.html', book_ticket=book_ticket)

    def is_accessible(self):
        return current_user.is_authenticated


class ReportMonth(BaseView):
    @expose('/', methods=['get', 'post'])
    def report_month(self):
        month_name = None

        if request.method == 'POST':
            month_name = request.form.get('month_name')

        report_month = utils.read_data_report_month(month_name)

        return self.render('admin/report-month.html', report_month=report_month, month_name=month_name)

    def is_accessible(self):
        return current_user.is_authenticated


class ReportYear(BaseView):
    @expose('/', methods=['get', 'post'])
    def report_year(self):
        year_name = None

        if request.method == 'POST':
            year_name = request.form.get('year_name')

        report_month = utils.read_data_report_month(year_name)

        report_year = utils.read_data_report_year(year_name)

        return self.render('admin/report-year.html', report_year=report_year, year_name=year_name)

    def is_accessible(self):
        return current_user.is_authenticated


# tao view xu li logout
class LogoutView(BaseView):
    @expose('/')
    def log_out(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


# tao view xu li sign up
# class SignUpView(BaseView):
#     @expose('/')
#     def sign_up(self):
#         return self.render('admin/sign-up.html')
#
#     def is_accessible(self):
#         return not current_user.is_authenticated
#
#
# admin.add_view(SignUpView(name='Sign Up'))

#Add view
admin.add_view(CustomerView(Customer, db.session, name='Khách hàng', category='Quản lý người dùng'))
admin.add_view(EmployeeView(Employee, db.session, name='Nhân viên', category='Quản lý người dùng'))
admin.add_view(AirportView(Airport, db.session, name='Sân bay', category='Quản lý sân bay'))
admin.add_view(
    IntermediateAirportView(IntermediateAirport, db.session, name='Sân bay trung gian', category='Quản lý sân bay'))
admin.add_view(PlaneView(Plane, db.session, name='Máy bay', category='Quản lý sân bay'))
admin.add_view(FlightView(Flight, db.session, name='Chuyến bay', category='Quản lý chuyến bay'))
admin.add_view(SeatView(Seat, db.session, name='Ghế ngồi', category='Quản lý chuyến bay'))
admin.add_view(TicketView(AirTicket, db.session, name='Vé', category='Quản lý chuyến bay'))
admin.add_view(BookTicketView(BookTicket, db.session, name='Phiếu đặt chỗ', category='Quản lý chuyến bay'))

# admin.add_view(ReportMonthView(ReportMonth, db.session, name='Báo cáo tháng', category='Báo cáo thống kê'))
# admin.add_view(ReportYearView(ReportYear, db.session, name='Báo cáo năm', category='Báo cáo thống kê'))

admin.add_view(ReportMonth(name='Báo cáo tháng', category='Báo cáo'))

admin.add_view(ReportYear(name='Báo cáo năm', category='Báo cáo'))

admin.add_view(ConfirmTicket(name='Xác nhận đặt vé'))

admin.add_view(UserView(User, db.session))

admin.add_view(Contact(name="Contact"))

admin.add_view(LogoutView(name="Logout"))