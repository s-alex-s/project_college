import datetime
import os
import openpyxl

from main.models import *
from project_college.settings import MEDIA_ROOT, DEFAULT_ACCOUNT_PASSWORD
from django.utils.translation import gettext_lazy as _


def check_teacher_pk(request, schedule):
    if request.user.pk not in list(map(lambda x: x.pk, schedule.teachers.all())):
        return False
    return True


def student_exist(username):
    if User.objects.filter(username=username):
        return True, _('Пользователь с таким логином уже существует')
    return False,


def add_student(student):
    exist = student_exist(student.username)
    if exist[0]:
        return exist

    student.save()
    user = User(student_profile=student, username=student.username)
    user.set_password(DEFAULT_ACCOUNT_PASSWORD)
    user.save()

    return True,


def excel_handler_topic(request):
    errors = []
    objects = []

    file_path = f'{MEDIA_ROOT}/files/excel/{request.user.pk}.xlsx'.replace("\\", "/")
    with open(file_path, 'wb+') as file:
        for chunk in request.FILES['excel_file'].chunks():
            file.write(chunk)

            excel = openpyxl.open(file, read_only=True)
            excel = excel.active

            # Кол-во часов, тема, что задано
            count = 2
            for i in list(excel)[1:]:
                hours = i[0].value

                topic = None
                try:
                    topic = i[1].value.strip()
                except AttributeError:
                    errors.append(_('Пустая ячейка') + f': столбец - 2; строка - {count}')

                homework = None
                try:
                    homework = i[2].value.strip()
                except AttributeError:
                    errors.append(_('Пустая ячейка') + f': столбец - 3; строка - {count}')

                if type(hours) is not int:
                    errors.append(_('Неверный формат данных') + f': столбец - 1; строка - {count}')

                count += 1
                objects.append((hours, topic, homework))
    os.remove(file_path)

    if not errors:
        for hours, topic, homework in objects:
            Topic(
                name=topic,
                hours=hours,
                home_task=homework,
                module_id=request.POST['module']
            ).save()

    return errors


def excel_handler_student(request):
    errors = []
    objects = []

    file_path = f'{MEDIA_ROOT}/files/excel/{request.user.pk}.xlsx'.replace("\\", "/")
    with open(file_path, 'wb+') as file:
        for chunk in request.FILES['excel_file'].chunks():
            file.write(chunk)

            excel = openpyxl.open(file, read_only=True)
            excel = excel.active

            # first name, last name, Отчество, Номер телефона, Число; месяц; год рождения, email,
            # Номер по поименной книге, Дата и № приказа о зачислении, Домашний адрес обучающегося, Движение контингента
            # Дополнительные сведения
            count = 2
            for i in list(excel)[1:]:
                username = None
                try:
                    username = i[0].value.strip()
                    st_exist = student_exist(username)
                    if st_exist[0]:
                        errors.append(st_exist[1] + ': ' +
                                      _('столбец') + ' - 1; ' + _('строка') + ' - ' + str(count))
                except AttributeError:
                    errors.append(
                        _('Пустая ячейка') + ': ' + _('столбец') + ' - 1; ' + _('строка') + ' - ' + str(count))

                first_name = None
                try:
                    first_name = i[1].value.strip()
                except AttributeError:
                    errors.append(_('Пустая ячейка') + ': ' + _('столбец') + ' - 1; ' + _('строка') + ' - ' + str(count))

                last_name = None
                try:
                    last_name = i[2].value.strip()
                except AttributeError:
                    errors.append(_('Пустая ячейка') + ': ' + _('столбец') + ' - 2; ' + _('строка') + ' - ' + str(count))

                middle_name = None
                if i[3].value:
                    middle_name = i[3].value.strip()

                phone_number = None
                if i[4].value:
                    phone_number = i[4].value.strip()

                birthday = None
                try:
                    if i[5].value:
                        if type(i[5].value) is str:
                            birthday = datetime.datetime.strptime(i[5].value.strip(), '%d.%m.%y')
                        elif type(i[5].value) is datetime.datetime:
                            birthday = datetime.datetime(year=i[5].value.year, month=i[5].value.month,
                                                         day=i[5].value.day)
                        birthday = datetime.date(birthday.year, birthday.month, birthday.day)
                except ValueError:
                    errors.append(_('Неверный формат даты, нужный формат - дд.мм.гг'))

                email = None
                if i[6].value:
                    email = i[6].value.strip()

                book_number = None
                if i[7].value:
                    book_number = i[7].value.strip()

                date_in = None
                if i[8].value:
                    date_in = i[8].value.strip()

                home_address = None
                if i[9].value:
                    home_address = i[9].value.strip()

                move = None
                if i[10].value:
                    move = i[10].value.strip()

                additional = None
                if i[11].value:
                    additional = i[11].value.strip()

                count += 1
                objects.append((username, first_name, last_name, middle_name, phone_number, birthday, email,
                                book_number, date_in, home_address, move, additional))
    os.remove(file_path)

    if not errors:
        for username, first_name, last_name, middle_name, phone_number, birthday, email, book_number, date_in, home_address, move, additional in objects:
            result = add_student(Student(
                username=username,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                phone_number=phone_number,
                birthday=birthday,
                email=email,
                number=book_number,
                enrollment_date=date_in,
                home_address=home_address,
                courses=move,
                additional_info=additional,
                group_id=request.POST['group']
            ))

            if not result[0]:
                errors.append(result[1])

    return errors
