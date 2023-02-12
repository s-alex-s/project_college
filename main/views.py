import datetime
import json
import openpyxl
import os

from django.http import FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from project_college.settings import MARKS_SYSTEM, MARK_VALUES, MARKS_RATING, MEDIA_ROOT
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import user_passes_test

from .forms import *
from .models import *
from .mixins import *
from .validators import *

from .functions import *


def page_not_found(request, exception):
    return render(request, 'main/404.html')


@login_required(login_url=reverse_lazy('login_page'))
def main_page(request):
    if request.user.is_superuser or request.user.is_junioradmin:
        return redirect('dashboard')
    elif request.user.is_teacher:
        return redirect('teacher-groups')
    elif request.user.student_profile:
        return redirect('student-modules')
    return redirect('logout')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('main_page')
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return redirect('main_page')
    else:
        form = UserLoginForm()

    return render(request, 'main/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('main_page')


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def dashboard(request):
    return render(request, 'main/dashboard.html', {'student_count': Student.objects.count(),
                                                   'teachers_count': User.objects.filter(is_teacher=True).count()})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def reset_password(request):
    if request.method == 'POST':
        form = ResetPassword(data=request.POST)
        if form.is_valid():
            return redirect('main_page')
    else:
        form = ResetPassword()
    return render(request, 'main/reset-password.html', {'form': form})


@login_required(login_url=reverse_lazy('login_page'))
def change_password(request):
    if request.method == 'POST':
        form = ChangePassword(user=request.user, data=request.POST)
        if form.is_valid():
            return redirect('main_page')
    else:
        form = ChangePassword()
    return render(request, 'main/change_password.html', {'form': form})


class UserProfileView(ViewsMixin, LoginRequiredMixin, StuffRequiredMixin, DetailView):
    model = User
    template_name = 'main/user-profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


class EditUserProfile(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = EditUserForm
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('user-profile')
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


# Schedule
class GroupsScheduleView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Group
    context_object_name = 'groups'
    template_name = 'main/schedule/groups-schedule.html'


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def days_schedule(request, pk):
    group = Group.objects.get(pk=pk)
    schedule = {
        '0': [],
        '1': [],
        '2': [],
        '3': [],
        '4': [],
        '5': [],
    }
    for i in Schedule.objects.filter(group__name=group.name).select_related('group', 'module').prefetch_related(
            'teachers'
    ):
        schedule[str(i.date)].append(i)
    return render(request, 'main/schedule/days-schedule.html',
                  {'days': DAY_NAMES,
                   'group': group,
                   'mon': schedule['0'],
                   'tue': schedule['1'],
                   'wed': schedule['2'],
                   'thu': schedule['3'],
                   'fri': schedule['4'],
                   'sat': schedule['5'],
                   })


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def edit_schedule(request, group_pk, sch_pk):
    group = Group.objects.get(pk=group_pk)
    sch = Schedule.objects.get(pk=sch_pk)

    if request.method == 'POST':
        form = ScheduleForm(data=request.POST, instance=sch)
        form.fields['teachers'].queryset = User.objects.filter(is_teacher=True)

        if form.is_valid():
            form.save()
            return redirect('days-schedule', pk=group_pk)
    else:
        form = ScheduleForm(instance=sch)
        form.fields['teachers'].queryset = User.objects.filter(is_teacher=True)
    return render(request, 'main/schedule/edit-schedule.html', {'form': form, 'group': group})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def delete_schedule(request, group_pk, sch_pk):
    sch = Schedule.objects.get(pk=sch_pk)

    if request.method == 'POST':
        sch.delete()
        return redirect('days-schedule', pk=group_pk)
    return render(request, 'main/delete-views/delete-form.html', {'object': sch})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def create_schedule(request, pk):
    group = Group.objects.get(pk=pk)

    if request.method == 'POST':
        form = ScheduleForm(data=request.POST)
        form.fields['teachers'].queryset = User.objects.filter(is_teacher=True)

        if form.is_valid():
            form.save()
            return redirect('days-schedule', pk=pk)
    else:
        form = ScheduleForm(initial={'group': group})
        form.fields['teachers'].queryset = User.objects.filter(is_teacher=True)
    return render(request, 'main/schedule/add-schedule.html', {'form': form, 'group': group})


# Teacher
class TeacherGroupsView(ViewsMixin, LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Group
    template_name = 'main/teacher/teacher-groups.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return set(map(lambda x: (x.group.pk, x.group.name),
                       Schedule.objects.filter(teachers__pk=self.request.user.pk).select_related('group')))


class TeacherNotificationsView(ViewsMixin, LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Notification
    template_name = 'main/teacher/notifications.html'
    context_object_name = 'notifs'

    def get_queryset(self):
        return Notification.objects.filter(for_teachers=True)


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_teacher, login_url=reverse_lazy('main_page'))
def teacher_modules(request, group_pk):
    group = Group.objects.get(pk=group_pk)
    schedule = {
        '0': [],
        '1': [],
        '2': [],
        '3': [],
        '4': [],
        '5': [],
    }
    for i in Schedule.objects.filter(group__name=group.name, teachers__pk=request.user.pk).select_related('module'):
        schedule[str(i.date)].append(i)
    return render(request, 'main/teacher/teacher-modules.html',
                  {'days': DAY_NAMES,
                   'group': group,
                   'mon': schedule['0'],
                   'tue': schedule['1'],
                   'wed': schedule['2'],
                   'thu': schedule['3'],
                   'fri': schedule['4'],
                   'sat': schedule['5'],
                   })


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def dismiss_student(request, pk):
    student = Student.objects.get(pk=pk)
    group_id = student.group_id

    if request.method == 'POST':
        dismissed_student = DismissedStudent(
            username=student.username,
            first_name=student.first_name,
            last_name=student.last_name,
            middle_name=student.middle_name,
            phone_number=student.phone_number,
            birthday=student.birthday,
            email=student.email,
            home_address=student.home_address,
            additional_info=student.additional_info
        )
        dismissed_student.save()
        student.delete()

        if group_id:
            return redirect('students-list', group_id=group_id)
        return redirect('students-list', group_id=0)
    else:
        return render(request, 'main/delete-views/dismiss-student.html', {'object': student})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def delete_student(request, pk):
    student = Student.objects.get(pk=pk)
    group_id = student.group_id

    if request.method == 'POST':
        student.user.delete()
        student.delete()

        if group_id:
            return redirect('students-list', group_id=group_id)
        return redirect('students-list', group_id=0)
    return render(request, 'main/delete-views/delete-form.html', {'object': student})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def recovery_student(request, pk):
    d_student = DismissedStudent.objects.get(pk=pk)
    if request.method == 'POST':
        student = Student(
            username=d_student.username,
            first_name=d_student.first_name,
            last_name=d_student.last_name,
            middle_name=d_student.middle_name,
            phone_number=d_student.phone_number,
            birthday=d_student.birthday,
            email=d_student.email,
            home_address=d_student.home_address,
            additional_info=d_student.additional_info
        )
        student.save()
        user = User.objects.get(username=student.username)
        user.student_profile = student
        user.save()
        d_student.delete()

        return redirect('edit-student', pk=student.pk)
    else:
        return render(request, 'main/delete-views/recovery-student.html', {'object': d_student})


# Teacher journal
@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_teacher, login_url=reverse_lazy('main_page'))
def teacher_journal(request, sch_pk):
    sch = Schedule.objects.select_related('module').prefetch_related('module__topic_set').get(pk=sch_pk)
    msg = None

    if not check_teacher_pk(request, sch):
        return redirect('main_page')

    # mark_id or topic_id, student_id; date, compl_topic_id or date, empty, topic_id;
    if request.method == 'POST':
        for key, value in request.POST.items():
            ids = key.split('_')
            value = value.strip()

            if ids[0] == 'date':
                if ids[1] == 'empty':
                    if value:
                        try:
                            date_time = datetime.datetime.strptime(value, '%d.%m.%y')
                            now = datetime.datetime.now()
                            date_time = date_time.replace(hour=now.hour,
                                                          minute=now.minute,
                                                          second=now.second)
                            compl_topic = CompletedTopic(
                                date_time=date_time,
                                topic_id=ids[2],
                                module_id=sch.module_id
                            )
                            compl_topic.teacher = request.user
                            compl_topic.save()
                        except ValueError:
                            msg = _('Неправильный формат даты, нужный формат: дд.мм.гг')
                else:
                    if value:
                        try:
                            date_time = datetime.datetime.strptime(value, '%d.%m.%y')
                            now = datetime.datetime.now()
                            date_time = date_time.replace(hour=now.hour,
                                                          minute=now.minute,
                                                          second=now.second)

                            compl_topic = CompletedTopic.objects.get(pk=ids[1])
                            compl_topic.date_time = date_time
                            compl_topic.teacher = request.user
                            compl_topic.save()
                        except ValueError:
                            pass
                    else:
                        CompletedTopic.objects.get(pk=ids[1]).delete()
            else:
                if len(ids) == 1:
                    if str(value) in MARK_VALUES:
                        new_mark = Mark.objects.get(pk=ids[0])
                        if value.isdigit():
                            if new_mark.mark != int(value):
                                new_mark.mark = int(value)
                                new_mark.teacher = request.user
                                new_mark.save()
                        elif new_mark.mark is not None:
                            new_mark.mark = None
                            new_mark.teacher = request.user
                            new_mark.save()
                    elif value == '':
                        Mark.objects.get(pk=ids[0]).delete()
                elif len(ids) == 2:
                    if str(value) in MARK_VALUES:
                        new_mark = Mark(
                            student_id=ids[1],
                            teacher_id=request.user.pk,
                            topic_id=ids[0],
                            module_id=sch.module_id,
                        )
                        if value.isdigit():
                            if new_mark.mark != int(value):
                                new_mark.mark = int(value)
                        elif new_mark.mark is not None:
                            new_mark.mark = None
                        new_mark.save()

    journal = {
        'students': sch.group.student_set.all(),
        'topics': [i for i in sch.module.topic_set.all()],
        'marks': []
    }
    total_hours = 0
    mid_marks = {}
    for topic in journal['topics']:
        topic_marks = []
        compl_topic = CompletedTopic.objects.filter(topic_id=topic.pk, module_id=sch.module_id)
        if compl_topic:
            topic_marks.append((topic, compl_topic.first(), 'date'))
        else:
            topic_marks.append((topic, ' ', 'date'))
        total_hours += topic.hours
        for student in journal['students']:
            if student.pk not in mid_marks.keys():
                mid_marks[student.pk] = []
            mark = Mark.objects.filter(module=sch.module, student=student, topic=topic).select_related('topic').first()
            if not mark:
                topic_marks.append((' ', student.pk))
            else:
                if mark.mark:
                    mid_marks[student.pk].append(mark.mark)
                topic_marks.append((mark.pk, mark.mark))
        journal['marks'].append(topic_marks)

    mid_marks = list(mid_marks.values())
    for n, i in enumerate(mid_marks):
        marks_sum = sum(mid_marks[n])
        if marks_sum:
            mid_marks[n] = round(marks_sum / len(mid_marks[n]), 1)
        else:
            mid_marks[n] = 0

    return render(request, 'main/teacher/journal.html', {
        'sch': sch,
        'total_hours': total_hours,
        'journal': journal,
        'mid_marks': mid_marks,
        'mark_values': {'data': MARK_VALUES},
        'marks_rating': MARKS_RATING,
        'msg': msg,
    })


# Student
class StudentModulesView(ViewsMixin, LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Schedule
    template_name = 'main/student/student-modules.html'
    context_object_name = 'sch'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        context['group'] = self.request.user.student_profile.group

        schedule = {
            '0': [],
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
        }
        for i in Schedule.objects.filter(group=context['group']).select_related('module'):
            schedule[str(i.date)].append(i)

        context['days'] = DAY_NAMES
        context['mon'] = schedule['0']
        context['tue'] = schedule['1']
        context['wed'] = schedule['2']
        context['thu'] = schedule['3']
        context['fri'] = schedule['4']
        context['sat'] = schedule['5']

        return context

    def get_queryset(self):
        return Schedule.objects.filter(group=self.request.user.student_profile.group)


class StudentNotificationsView(ViewsMixin, LoginRequiredMixin, StudentRequiredMixin, ListView):
    model = Notification
    template_name = 'main/student/notifications.html'
    context_object_name = 'notifs'

    def get_queryset(self):
        return Notification.objects.filter(for_students=True)


class StudentMarksView(ViewsMixin, LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = Schedule
    template_name = 'main/student/student-marks.html'
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['marks_rating'] = MARKS_RATING

        return context

    def get_object(self, queryset=None):
        schedule = Schedule.objects.get(pk=self.kwargs['sch_pk'])
        data = {'tables': [], 'module_name': schedule.module.__str__(), 'teachers': schedule.teachers.all()}
        table = {'marks': []}

        for topic in schedule.module.topic_set.all():
            try:
                table['marks'].append({'title': topic.__str__(),
                                       'mark': topic.mark_set.get(
                                           student__pk=self.request.user.student_profile.pk).mark})
            except ObjectDoesNotExist:
                table['marks'].append({'title': topic.__str__(),
                                       'mark': ' '})
        data['tables'].append(table)

        return data


class StudentProfileView(ViewsMixin, LoginRequiredMixin, StudentRequiredMixin, DetailView):
    model = Student
    template_name = 'main/user-profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user.student_profile


# List Views
class DismissedStudentsView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = DismissedStudent
    template_name = 'main/list-views/dismissed-students.html'
    context_object_name = 'students'


class NotificationsAdminView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Notification
    template_name = 'main/notifications.html'
    context_object_name = 'notifs'


class TeachersView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'main/list-views/teachers-list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        return User.objects.filter(is_teacher=True, is_junioradmin=False, is_superuser=False)


class StudentsWithoutGroup(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Student
    template_name = 'main/list-views/students-list.html'
    context_object_name = 'students'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = _('Без группы')

        return context

    def get_queryset(self):
        return Student.objects.filter(group_id=None)


class StudentsViewGroups(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Group
    template_name = 'main/list-views/students-list-groups.html'
    context_object_name = 'groups'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['no_group_students'] = Student.objects.filter(group_id=None)

        return context


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def students_view(request, group_id):
    if not group_id:
        return redirect('no-group-students-list')

    return render(request, 'main/list-views/students-list.html',
                  {'students': Student.objects.filter(group_id=group_id),
                   'group': Group.objects.get(pk=group_id)})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def add_student_from_file(request):
    if request.method == 'POST':
        form = AddStudentsFileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            errors = excel_handler_student(request)
            if not errors:
                return redirect('students-list', int(form.data['group'][0]))
            else:
                for error in errors:
                    form.add_error('excel_file', error)
    else:
        form = AddStudentsFileForm()
    return render(request, 'main/create-views/student-excel.html', {'form': form})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def download_pattern_student(request):
    return FileResponse(open(f'{MEDIA_ROOT}/files/excel/student-pattern.xlsx', 'rb'), as_attachment=True)


class GroupsView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Group
    template_name = 'main/list-views/groups-list.html'
    context_object_name = 'groups'


class ModulesView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Module
    template_name = 'main/list-views/modules-list.html'
    context_object_name = 'modules'


class TopicsViewModules(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Module
    template_name = 'main/list-views/topics-list-modules.html'
    context_object_name = 'modules'


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def topics_view(request, module_id):
    return render(request, 'main/list-views/topics-list.html', {'topics': Topic.objects.filter(module_id=module_id),
                                                                'module': Module.objects.get(pk=module_id)})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def add_topic_from_file(request):
    if request.method == 'POST':
        form = AddTopicsFileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            errors = excel_handler_topic(request)
            if not errors:
                return redirect('topics-list')
            else:
                for error in errors:
                    form.add_error('excel_file', error)
    else:
        form = AddTopicsFileForm()
    return render(request, 'main/create-views/topic-excel.html', {'form': form})


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def download_pattern_topic(request):
    return FileResponse(open(f'{MEDIA_ROOT}/files/excel/topic-pattern.xlsx', 'rb'), as_attachment=True)


class QualificationsView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Qualification
    template_name = 'main/list-views/qualifications-list.html'
    context_object_name = 'quals'


class SpecializationsView(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Specialization
    template_name = 'main/list-views/specializations-list.html'
    context_object_name = 'specs'


# Create Views
class AddNotification(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Notification
    fields = '__all__'
    template_name = 'main/create-views/add-form.html'
    success_url = reverse_lazy('notifs-admin')


class AddUser(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, CreateView):
    form_class = UserForm
    template_name = 'main/create-views/add-form.html'
    success_url = reverse_lazy('teachers-list')


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def add_student(request, group_id):
    if request.method == 'POST':
        form = StudentForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('students-list', group_id=int(form.data['group']))
    else:
        form = StudentForm()
        form.initial = {'group': group_id}
    return render(request, 'main/create-views/add-form.html', {'form': form})


class AddGroup(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Group
    fields = '__all__'
    template_name = 'main/create-views/add-form.html'
    success_url = reverse_lazy('groups-list')


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def add_topic(request, module_id):
    if request.method == 'POST':
        form = TopicForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('topics-list', module_id=int(form.data['module']))
    else:
        form = TopicForm()
        form.initial = {'module': module_id}
    return render(request, 'main/update-views/update-form.html', {'form': form})


class AddModule(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Module
    fields = '__all__'
    template_name = 'main/create-views/add-form.html'
    success_url = reverse_lazy('modules-list')


class AddQualification(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Qualification
    fields = '__all__'
    template_name = 'main/create-views/add-form.html'
    success_url = reverse_lazy('quals-list')


class AddSpecialization(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Specialization
    fields = '__all__'
    template_name = 'main/create-views/add-form.html'
    success_url = reverse_lazy('specs-list')


# Update Views
class EditNotification(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Notification
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('notifs-admin')
    context_object_name = 'notif'
    fields = '__all__'


class EditUser(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = EditUserForm
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('teachers-list')
    context_object_name = 'user'


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def edit_student(request, pk):
    student = Student.objects.get(pk=pk)

    if request.method == 'POST':
        form = EditStudentForm(data=request.POST, instance=student)

        if form.is_valid():
            form.save()
            if form.data['group']:
                return redirect('students-list', group_id=int(form.data['group']))
            return redirect('no-group-students-list')
    else:
        form = EditStudentForm(instance=student)
    return render(request, 'main/update-views/update-form.html', {'form': form})


class EditGroup(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Group
    fields = '__all__'
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('groups-list')


class EditModule(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Module
    fields = '__all__'
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('modules-list')


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def edit_topic(request, pk):
    topic = Topic.objects.get(pk=pk)

    if request.method == 'POST':
        form = TopicForm(data=request.POST, instance=topic)

        if form.is_valid():
            form.save()
            return redirect('topics-list', module_id=int(form.data['module']))
    else:
        form = TopicForm(instance=topic)
    return render(request, 'main/update-views/update-form.html', {'form': form})


class EditQualification(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Qualification
    fields = '__all__'
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('quals-list')


class EditSpecialization(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Specialization
    fields = '__all__'
    template_name = 'main/update-views/update-form.html'
    success_url = reverse_lazy('specs-list')


# Delete Views
class DeleteNotification(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Notification
    template_name = 'main/delete-views/delete-form.html'
    success_url = reverse_lazy('notifs-admin')


class DeleteUser(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'main/delete-views/delete-form.html'
    success_url = reverse_lazy('teachers-list')


class DeleteGroup(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Group
    template_name = 'main/delete-views/delete-form.html'
    success_url = reverse_lazy('groups-list')


class DeleteModule(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Module
    template_name = 'main/delete-views/delete-form.html'
    success_url = reverse_lazy('modules-list')


@login_required(login_url=reverse_lazy('login_page'))
@user_passes_test(only_admin, login_url=reverse_lazy('main_page'))
def delete_topic(request, pk):
    topic = Topic.objects.get(pk=pk)
    module_id = topic.module_id

    if request.method == 'POST':
        topic.delete()

        return redirect('topics-list', module_id=module_id)
    return render(request, 'main/delete-views/delete-form.html', {'object': topic})


class DeleteQualification(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Qualification
    template_name = 'main/delete-views/delete-form.html'
    success_url = reverse_lazy('quals-list')


class DeleteSpecialization(ViewsMixin, LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Specialization
    template_name = 'main/delete-views/delete-form.html'
    success_url = reverse_lazy('specs-list')
