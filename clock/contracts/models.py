from django.conf import settings
from django.db import models

from clock.contracts.fields import WorkingHoursField


class Contract(models.Model):
    """
    Employees may define a contract, which is assigned to a finished shift.
    """
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    department = models.CharField(max_length=200)
    department_short = models.CharField(max_length=100, blank=True, null=True)
    hours = WorkingHoursField()
    contact = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.department
