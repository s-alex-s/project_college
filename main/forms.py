from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from project_college.settings import DEFAULT_ACCOUNT_PASSWORD
from .models import *


class UserLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _('Неправильный логин или пароль')
    }

    username = forms.CharField(label=_('Логин'), label_suffix='', widget=forms.TextInput(attrs={'class': 'form-item',
                                                                                                'autocomplete': 'off',
                                                                                                'autofocus': 'on'}),)
    password = forms.CharField(label=_('Пароль'), label_suffix='',
                               widget=forms.PasswordInput(attrs={'class': 'form-item'}))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number',
                  'is_teacher',
                  'is_junioradmin']
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': 'on'})
        }
        help_texts = {
            'username': _(
                f'При добавлении пользователя пароль автоматически установится на: {DEFAULT_ACCOUNT_PASSWORD}')
        }

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['is_teacher'] and not cleaned_data['is_junioradmin']:
            raise ValidationError(_('Укажите кем является пользователь'))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(DEFAULT_ACCOUNT_PASSWORD)
        if commit:
            user.save()
        return user


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'middle_name', 'email', 'phone_number',
                  'is_teacher',
                  'is_junioradmin']
        widgets = {
            'username': forms.TextInput(attrs={'autofocus': 'on'})
        }

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['is_teacher'] and not cleaned_data['is_junioradmin']:
            raise ValidationError(_('Укажите кем является пользователь'))
        return cleaned_data


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        help_texts = {
            'username': _(
                f'При добавлении пользователя пароль автоматически установится на: {DEFAULT_ACCOUNT_PASSWORD}')
        }

        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'username': forms.TextInput(attrs={'autofocus': 'on'})
        }

    def clean(self):
        cleaned_data = super().clean()
        if User.objects.filter(username=cleaned_data['username']):
            raise ValidationError(_('Пользователь с таким логином уже существует'))
        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)

        if commit:
            student.save()
        try:
            student.user.username = student.username
            if commit:
                student.user.save()
        except ObjectDoesNotExist:
            user = User(student_profile=student, username=student.username)
            user.set_password(DEFAULT_ACCOUNT_PASSWORD)
            if commit:
                user.save()

        return student


class EditStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'username': forms.TextInput(attrs={'autofocus': 'on'})
        }

    def clean(self):
        cleaned_data = super().clean()
        if self.instance.username != cleaned_data['username'] and User.objects.filter(username=cleaned_data['username']):
            raise ValidationError(_('Пользователь с таким логином уже существует'))
        return cleaned_data

    def save(self, commit=True):
        student = super().save(commit=False)

        student.user.username = student.username
        if commit:
            student.save()
            student.user.save()

        return student


class ResetPassword(forms.Form):
    username = forms.CharField(max_length=150, label_suffix='', label=_('Логин'),
                               help_text=_('Введите логин пользователя для которого хотите сбросить пароль. '
                                           f'Пароль будет сброшен на {DEFAULT_ACCOUNT_PASSWORD}'),
                               widget=forms.TextInput(attrs={'autofocus': 'on'}))

    def clean(self):
        cleaned_data = super().clean()
        try:
            user = User.objects.get(username=cleaned_data['username'])
        except ObjectDoesNotExist:
            raise ValidationError(_('Пользователя с таким логином не существует'))

        user.set_password(DEFAULT_ACCOUNT_PASSWORD)
        user.save()
        return cleaned_data


class ChangePassword(forms.Form):
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.current_user = user

    old_password = forms.CharField(max_length=128, label_suffix='', label=_('Текущий пароль'),
                                   widget=forms.PasswordInput(attrs={'autofocus': 'on'}))
    new_password = forms.CharField(max_length=128, label_suffix='', label=_('Новый пароль'),
                                   widget=forms.PasswordInput())
    repeat_new_password = forms.CharField(max_length=128, label_suffix='', label=_('Повторите новый пароль'),
                                          widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        if not self.current_user.check_password(cleaned_data['old_password']):
            raise ValidationError(_('Неправильный текущий пароль'))
        if cleaned_data['new_password'] != cleaned_data['repeat_new_password']:
            raise ValidationError(_('Пароли не совпадают'))
        self.current_user.set_password(cleaned_data['new_password'])
        self.current_user.save()
        return cleaned_data


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'

        help_texts = {
            'teachers': _('Для выбора нескольких преподавателей зажмите Ctrl')
        }

        widgets = {
            'module': forms.Select(attrs={'autofocus': 'on'}),
            'time_start': forms.TimeInput(attrs={'type': 'time'}),
            'time_end': forms.TimeInput(attrs={'type': 'time'}),
            'group': forms.HiddenInput()
        }


class AddTopicsFileForm(forms.Form):
    module = forms.ModelChoiceField(queryset=Module.objects.get_queryset(), label=_('Предмет'))
    excel_file = forms.FileField(label=_('Excel файл'))

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['excel_file'].__str__().endswith('.xlsx'):
            raise ValidationError(_('Неверный формат файла'))

        return cleaned_data


class AddStudentsFileForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.get_queryset(), label=_('Группа'))
    excel_file = forms.FileField(label=_('Excel файл'))

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data['excel_file'].__str__().endswith('.xlsx'):
            raise ValidationError(_('Неверный формат файла'))

        return cleaned_data
