from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager


class Shift(models.Model):
    """
    Employees begin and finish shifts to track their worktime.
    May be assigned to a contract.
    """

    KEY_CHOICES = ((_('S'), _('Sick')), (_('V'), _('Vacation')))

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('Contract')
    )
    started = models.DateTimeField(verbose_name=_('Shift started'))
    finished = models.DateTimeField(
        null=True, verbose_name=_('Shift finished')
    )
    bool_finished = models.BooleanField(
        default=False, verbose_name=_('Shift completed?')
    )
    duration = models.DurationField(
        blank=True, null=True, verbose_name=_('Shift duration')
    )
    pause_started = models.DateTimeField(blank=True, null=True)
    pause_duration = models.DurationField(
        default=timedelta(seconds=0), verbose_name=_('Pause duration')
    )
    key = models.CharField(
        _('Key'), max_length=2, choices=KEY_CHOICES, blank=True
    )
    note = models.TextField(_('Note'), blank=True)
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-finished']

    def __str__(self):
        """
        Class returns the employees name as default.
        """
        return str(self.employee)

    @property
    def is_finished(self):
        """Return True if `Shift` is finished. Otherwise return False.

        Note: We need the extra `or False`, as this function would otherwise
        return `None`.
        """
        return bool(self.finished) or False

    @property
    def current_duration(self):
        return timezone.now() - self.started

    @property
    def contract_or_none(self):
        """Return the name of the contract or None."""
        if self.contract:
            return self.contract.department
        return None
