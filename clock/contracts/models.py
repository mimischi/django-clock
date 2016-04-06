from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from clock.contracts.fields import WorkingHoursField


class Contract(models.Model):
    """
    Employees may define a contract, which is assigned to a finished shift.
    """
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    department = models.CharField(max_length=200, verbose_name=_('Department'))
    department_short = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Abbreviation'))
    hours = WorkingHoursField(verbose_name=_('Work hours'))
    contact = models.EmailField(blank=True, verbose_name=_('Contract'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.department
