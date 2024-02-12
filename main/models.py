from django.urls import reverse
from django.utils.translation import gettext as _

from django.db import models
from django.contrib.auth.models import AbstractUser

from project_college.settings import DAY_NAMES
from .validators import correct_mark
from django.contrib.auth.validators import UnicodeUsernameValidator


class Specialization(models.Model):
    code = models.CharField(max_length=100, verbose_name=_('Код специализации'), db_index=True)
    name = models.CharField(max_length=200, verbose_name=_('Имя специализации'), db_index=True)

    def __str__(self):
        return f'{_("Код")}: {self.code}, {_("Имя")}: {self.name}'

    def get_absolute_url(self):
        return reverse('edit-spec', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Специализация')
        verbose_name_plural = _('Специализации')
        ordering = ['name']


class Qualification(models.Model):
    code = models.CharField(max_length=100, verbose_name=_('Код квалификации'), db_index=True)
    name = models.CharField(max_length=200, verbose_name=_('Имя квалификации'), db_index=True)

    def __str__(self):
        return f'{_("Код")}: {self.code}, {_("Имя")}: {self.name}'

    def get_absolute_url(self):
        return reverse('edit-qual', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Квалификация')
        verbose_name_plural = _('Квалификации')
        ordering = ['name']


class Topic(models.Model):
    name = models.CharField(max_length=150, verbose_name=_('Имя темы'), db_index=True)
    hours = models.PositiveSmallIntegerField(verbose_name=_('Количество учебных часов'), default=0)
    home_task = models.TextField(verbose_name=_('Что задано'), blank=True, null=True)

    module = models.ForeignKey('Module', on_delete=models.CASCADE, verbose_name=_('Предмет'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('edit-topic', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Тема')
        verbose_name_plural = _('Темы')
        ordering = ['module', 'name']


class Module(models.Model):
    module_index = models.CharField(max_length=20, verbose_name=_('Индекс предмета'), null=True, blank=True,
                                    db_index=True)
    module_name = models.CharField(max_length=100, verbose_name=_('Наименование предмета'), db_index=True)
    hours_1 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 1 семестре'), default=0)
    hours_2 = models.PositiveSmallIntegerField(verbose_name=_('Часов во 2 семестре'), default=0)
    hours_3 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 3 семестре'), default=0)
    hours_4 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 4 семестре'), default=0)
    hours_5 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 5 семестре'), default=0)
    hours_6 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 6 семестре'), default=0)
    hours_7 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 7 семестре'), default=0)
    hours_8 = models.PositiveSmallIntegerField(verbose_name=_('Часов в 8 семестре'), default=0)
    exam_type = models.CharField(max_length=200, verbose_name=_('Форма итоговой атестации'), choices=[
        (None, _('Выберите форму итоговой аттестации')),
        ('e', _('Экзамен')),
        ('z', _('Зачет'))
    ])

    specializations = models.ManyToManyField(Specialization, verbose_name=_('Специализации'), blank=True)
    qualifications = models.ManyToManyField(Qualification, verbose_name=_('Квалификации'), blank=True)

    def __str__(self):
        output = ''
        if self.module_index:
            output += f'{self.module_index} '
        output += self.module_name

        return output

    def get_hours(self):
        return self.hours_1 + self.hours_2 + self.hours_3 + self.hours_4 + self.hours_5 + self.hours_6 + self.hours_7 + self.hours_8

    def get_absolute_url(self):
        return reverse('edit-module', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Модуль')
        verbose_name_plural = _('Модули')
        ordering = ['module_name']


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("Логин"),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)
    middle_name = models.CharField(_("Отчество"), max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=12, verbose_name=_('Номер телефона'), blank=True, db_index=True,
                                    null=True)
    is_teacher = models.BooleanField(default=False, verbose_name=_('Права учителя'))
    is_junioradmin = models.BooleanField(default=False, verbose_name=_('Права администратора'))

    student_profile = models.OneToOneField('Student', on_delete=models.SET_NULL, verbose_name=_('Профиль студента'),
                                           null=True, blank=True)

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        output =  f'{self.last_name} {self.first_name}'
        if self.middle_name:
            output += ' ' + self.middle_name
        return output

    def get_absolute_url(self):
        return reverse('edit-user', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['last_name']


class Schedule(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, verbose_name=_('Группа'))
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, verbose_name=_('Предмет'), null=True)
    teachers = models.ManyToManyField(User, verbose_name=_('Преподаватели'))
    date = models.PositiveSmallIntegerField(verbose_name=_('День недели'), choices=[
        (None, _('Выберите день недели')),
        (0, DAY_NAMES[0]),
        (1, DAY_NAMES[1]),
        (2, DAY_NAMES[2]),
        (3, DAY_NAMES[3]),
        (4, DAY_NAMES[4]),
        (5, DAY_NAMES[5])
    ])
    time_start = models.TimeField(verbose_name=_('Время начала'), blank=True, null=True)
    time_end = models.TimeField(verbose_name=_('Время конца'), blank=True, null=True)

    def __str__(self):
        return f'{DAY_NAMES[self.date]}, {self.group.name}; {_("Предмет")}: {self.module.module_name}; ' \
               f'{_("Преподаватели")}: ' \
               f'{", ".join(list(map(lambda x: x.first_name, list(self.teachers.all()))))}'

    class Meta:
        verbose_name = _('Содержание')
        verbose_name_plural = _('Содержание')
        ordering = ['time_start', 'time_end']


class Student(models.Model):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("Логин"),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, db_index=True)
    last_name = models.CharField(_("last name"), max_length=150, db_index=True)
    middle_name = models.CharField(_("Отчество"), max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=12, verbose_name=_('Номер телефона'), blank=True, db_index=True,
                                    null=True)
    birthday = models.DateField(verbose_name=_('Число, месяц, год рождения'), blank=True, null=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    number = models.PositiveSmallIntegerField(verbose_name=_('Номер по поименной книге'), blank=True, null=True,
                                              db_index=True)
    enrollment_date = models.CharField(max_length=300, verbose_name=_('Дата и № приказа о зачислении'), blank=True,
                                       null=True)
    home_address = models.CharField(max_length=200, verbose_name=_('Домашний адрес обучающегося'), blank=True,
                                    null=True)
    courses = models.CharField(max_length=100, verbose_name=_('Движение контингента'), blank=True, null=True)
    additional_info = models.TextField(verbose_name=_('Дополнительные сведения'), blank=True, null=True)

    group = models.ForeignKey('Group', on_delete=models.SET_NULL, verbose_name=_('Группа'), null=True, blank=True)

    def __str__(self):
        output = f'{self.last_name} {self.first_name}'
        if self.middle_name:
            output += ' ' + self.middle_name
        return output

    def get_absolute_url(self):
        return reverse('edit-student', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Студент')
        verbose_name_plural = _('Студенты')
        ordering = ['last_name', 'first_name', 'middle_name']


class DismissedStudent(models.Model):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("Логин"),
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(_("first name"), max_length=150, db_index=True)
    last_name = models.CharField(_("last name"), max_length=150, db_index=True)
    middle_name = models.CharField(_("Отчество"), max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=12, verbose_name=_('Номер телефона'), blank=True, db_index=True,
                                    null=True)
    birthday = models.DateField(verbose_name=_('Число, месяц, год рождения'), blank=True, null=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    dismiss_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата отчисления'))
    home_address = models.CharField(max_length=200, verbose_name=_('Домашний адрес обучающегося'), blank=True,
                                    null=True)
    additional_info = models.TextField(verbose_name=_('Дополнительные сведения'), blank=True, null=True)

    def __str__(self):
        output = f'{self.last_name} {self.first_name}'
        if self.middle_name:
            output += ' ' + self.middle_name
        return output

    class Meta:
        verbose_name = _('Отчисленный студент')
        verbose_name_plural = _('Отчисленные студенты')
        ordering = ['last_name', 'first_name', 'middle_name']


class Group(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('Название группы'), unique=True, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('edit-group', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Группа')
        verbose_name_plural = _('Группы')
        ordering = ['name']


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name=_('Студент'))
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name=_('Учитель'), null=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name=_('Тема'))
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, verbose_name=_('Предмет'), null=True)
    date_time = models.DateTimeField(verbose_name=_('Дата и время'), auto_now=True)
    mark = models.PositiveSmallIntegerField(verbose_name=_('Оценка'), validators=[correct_mark], null=True)

    def __str__(self):
        if not self.mark:
            return _(f'Студент: {self.student}; Оценка: "не присутствовал"; Предмет: {self.module}; Тема: {self.topic}')
        return _(f'Студент: {self.student}; Оценка: {self.mark}; Предмет: {self.module}; Тема: {self.topic}')

    class Meta:
        verbose_name = _('Оценка')
        verbose_name_plural = _('Оценки')
        ordering = ['topic']


class Notification(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    content = models.TextField(verbose_name=_('Текст'))
    for_students = models.BooleanField(verbose_name=_('Для студентов'), default=False)
    for_teachers = models.BooleanField(verbose_name=_('Для учителей'), default=False)

    def __str__(self):
        return f'{_("Дата")}: {self.date_time.strftime("%d/%m/%Y %H:%M")}, {_("Текст")}: {self.content}'

    def get_absolute_url(self):
        return reverse('edit-notif', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _('Объявление')
        verbose_name_plural = _('Объявления')
        ordering = ['-date_time']


class CompletedTopic(models.Model):
    date_time = models.DateTimeField(verbose_name=_('Дата'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, verbose_name=_('Тема'))
    teacher = models.ForeignKey(User, verbose_name=_('Преподаватель'), on_delete=models.SET_NULL, null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, verbose_name=_('Предмет'), null=True)

    class Meta:
        verbose_name = _('Пройденная тема')
        verbose_name_plural = _('Пройденные темы')

    def __str__(self):
        return f'{self.date_time.strftime("%d/%m/%Y %H:%M")}, {self.module}, {self.topic} - {self.teacher}'
