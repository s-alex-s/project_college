from django.urls import path
from .views import *

urlpatterns = [
    path('', main_page, name='main_page'),
    path('login', login_page, name='login_page'),
    path('logout', user_logout, name='logout'),
    path('change-password', change_password, name='change-password'),
    path('reset-password', reset_password, name='reset-password'),
    path('user-profile', UserProfileView.as_view(), name='user-profile'),
    path('edit/user-profile', EditUserProfile.as_view(), name='edit-user-profile'),
    path('recovery-student/<int:pk>', recovery_student, name='recovery-student'),
    # Teacher journal
    path('teacher/schedule/<int:sch_pk>/journal', teacher_journal, name='teacher-journal'),
    # Schedule
    path('schedule/groups', GroupsScheduleView.as_view(), name='groups-schedule'),
    path('schedule/group/<int:pk>/days', days_schedule, name='days-schedule'),
    path('schedule/group/<int:pk>/create', create_schedule, name='create-schedule'),
    path('schedule/group/<int:group_pk>/edit/<int:sch_pk>', edit_schedule, name='edit-schedule'),
    path('schedule/group/<int:group_pk>/delete/<int:sch_pk>', delete_schedule, name='delete-schedule'),
    # View
    # Admin
    path('dismissed-students', DismissedStudentsView.as_view(), name='dismissed-students'),
    path('notifications-admin', NotificationsAdminView.as_view(), name='notifs-admin'),
    path('teachers', TeachersView.as_view(), name='teachers-list'),
    path('students-groups', StudentsViewGroups.as_view(), name='students-groups'),
    path('students/group/<int:group_id>', students_view, name='students-list'),
    path('students', StudentsWithoutGroup.as_view(), name='no-group-students-list'),
    path('dashboard', dashboard, name='dashboard'),
    path('groups', GroupsView.as_view(), name='groups-list'),
    path('modules', ModulesView.as_view(), name='modules-list'),
    path('topics-modules', TopicsViewModules.as_view(), name='topics-modules'),
    path('topics/module/<int:module_id>', topics_view, name='topics-list'),
    path('qualifications', QualificationsView.as_view(), name='quals-list'),
    path('specializations', SpecializationsView.as_view(), name='specs-list'),
    # Teacher
    path('teacher/groups', TeacherGroupsView.as_view(), name='teacher-groups'),
    path('teacher/notifications', TeacherNotificationsView.as_view(), name='teacher-notifs'),
    path('teacher/group/<int:group_pk>/modules', teacher_modules, name='teacher-modules'),
    # Student
    path('student/modules', StudentModulesView.as_view(), name='student-modules'),
    path('student/notifications', StudentNotificationsView.as_view(), name='student-notifs'),
    path('student/schedule/<int:sch_pk>/marks', StudentMarksView.as_view(), name='student-marks'),
    path('student/profile', StudentProfileView.as_view(), name='student-profile'),
    # Add
    path('add/notification', AddNotification.as_view(), name='add-notif'),

    path('add/user', AddUser.as_view(), name='add-user'),

    path('add/student/group/<int:group_id>', add_student, name='add-student'),
    path('add/student/file', add_student_from_file, name='add-student-file'),
    path('download/students-pattern', download_pattern_student, name='student-pattern-page'),

    path('add/group', AddGroup.as_view(), name='add-group'),

    path('add/module', AddModule.as_view(), name='add-module'),

    path('add/topic/module/<int:module_id>', add_topic, name='add-topic'),
    path('add/topic/file', add_topic_from_file, name='add-topic-file'),
    path('download/topics-pattern', download_pattern_topic, name='topic-pattern-page'),

    path('add/qualification', AddQualification.as_view(), name='add-qual'),

    path('add/specialization', AddSpecialization.as_view(), name='add-spec'),
    # Edit
    path('edit/notification/<int:pk>', EditNotification.as_view(), name='edit-notif'),
    path('edit/user/<int:pk>', EditUser.as_view(), name='edit-user'),
    path('edit/student/<int:pk>', edit_student, name='edit-student'),
    path('edit/group/<int:pk>', EditGroup.as_view(), name='edit-group'),
    path('edit/module/<int:pk>', EditModule.as_view(), name='edit-module'),
    path('edit/topic/<int:pk>', edit_topic, name='edit-topic'),
    path('edit/qualification/<int:pk>', EditQualification.as_view(), name='edit-qual'),
    path('edit/specialization/<int:pk>', EditSpecialization.as_view(), name='edit-spec'),
    # Delete
    path('dismiss/student/<int:pk>', dismiss_student, name='dismiss-student'),
    path('delete/notification/<int:pk>', DeleteNotification.as_view(), name='delete-notif'),
    path('delete/user/<int:pk>', DeleteUser.as_view(), name='delete-user'),
    path('delete/student/<int:pk>', delete_student, name='delete-student'),
    path('delete/group/<int:pk>', DeleteGroup.as_view(), name='delete-group'),
    path('delete/module/<int:pk>', DeleteModule.as_view(), name='delete-module'),
    path('delete/topic/<int:pk>', delete_topic, name='delete-topic'),
    path('delete/qualification/<int:pk>', DeleteQualification.as_view(), name='delete-qual'),
    path('delete/specialization/<int:pk>', DeleteSpecialization.as_view(), name='delete-spec'),
]
