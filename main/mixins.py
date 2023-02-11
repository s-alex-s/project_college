from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import *


class ViewsMixin:
    login_url = reverse_lazy('login_page')


class TeacherRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_teacher:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.student_profile:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_junioradmin and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class StuffRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_junioradmin and not request.user.is_teacher:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
