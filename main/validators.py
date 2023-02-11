from django.core.exceptions import ValidationError
from project_college.settings import MARKS_SYSTEM
from django.utils.translation import gettext_lazy as _


def correct_mark(mark):
    if not mark <= MARKS_SYSTEM:
        raise ValidationError(_('Оценка должна быть не выше ') + str(MARKS_SYSTEM))


def only_admin(user):
    return user.is_superuser or user.is_junioradmin


def only_teacher(user):
    return user.is_teacher
