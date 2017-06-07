from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fullname = models.CharField(_('Full name'), max_length=255, blank=True)
    language = models.CharField(
        _('Site language'),
        max_length=2,
        choices=settings.LANGUAGES,
        default='de')
