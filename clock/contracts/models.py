from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from clock.contracts.fields import WorkingHoursField
from clock.shifts.models import Shift
from clock.contracts.utils import convert_work_hours


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
        return unicode(self.department)

    def total_hours_per_contract(self):
        shifts = Shift.objects.filter(contract=self.pk)

        total_work_hours = timedelta(seconds=0)
        for shift in shifts:
            total_work_hours += shift.shift_duration
        return total_work_hours

    def completed_hours_per_month(self, date=datetime.today()):
        shifts = Shift.objects.filter(contract=self.pk,
                                      shift_started__year=date.year,
                                      shift_started__month=date.month,
                                      shift_finished__isnull=False)

        monthly_work_hours = timedelta(seconds=0)
        for shift in shifts:
            monthly_work_hours += shift.shift_duration

        hours, minutes = divmod(monthly_work_hours.total_seconds()/60, 60)
        return "%02d.%02d" % (hours, minutes)

    def completed_work_hours_percentage(self, date=datetime.today()):
        contract_hours = float(convert_work_hours(self.hours))
        completed_hours = float(convert_work_hours(self.completed_hours_per_month(date)))

        if completed_hours == 0:
            return 0
        return int(completed_hours / contract_hours * 100)
        # return '{:.1f}'.format(completed_hours / contract_hours * 100)
