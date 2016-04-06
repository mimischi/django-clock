from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from clock.contracts.models import Contract


class Shift(models.Model):
    """
    Employees start/pause/stop shifts to track their worktime.
    May be assigned to a contract.
    """
    employee = models.ForeignKey(settings.AUTH_USER_MODEL)
    contract = models.ForeignKey(
        Contract,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    shift_started = models.DateTimeField(verbose_name=_('Shift started'))
    shift_finished = models.DateTimeField(
        null=True,
        verbose_name=_('Shift finished')
    )
    shift_duration = models.DurationField(
        blank=True,
        null=True,
        verbose_name=_('Shift duration')
    )
    pause_started = models.DateTimeField(blank=True, null=True)
    pause_duration = models.DurationField(
        default=timedelta(seconds=0),
        verbose_name=_('Pause duration')
    )
    note = models.TextField(_('Note'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['shift_finished']

    def __unicode__(self):
        """
        Class returns the employees name as default.
        """
        return str(self.employee)

    def __init__(self, *args, **kwargs):
        """
        Initialize the model with the old shift_started/shift_finished values,
        so we can compare them with the new ones in the save() method.
        """
        super(Shift, self).__init__(*args, **kwargs)
        self.__old_shift_started = self.shift_started
        self.__old_shift_finished = self.shift_finished
        self.__old_pause_duration = self.pause_duration
        self.__old_shift_duration = self.shift_duration

    def clean(self, *args, **kwargs):
        """
        Run the super clean() method and the custom validation that we need.
        """
        super(Shift, self).clean(*args, **kwargs)
        self.shift_time_validation()

    def save(self, *args, **kwargs):
        """
        If either the shift_finished or shift_started values were changed,
        then we'll calculate the shift_duration. Also substract the
        pause_duration while we're at it. This accounts for both the
        quick-action buttons and manual edits in the admin-backend
        or dashboard-frontend.
        """
        # Lets check if this shift is just being updated
        if self.pk is not None and (self.shift_finished != self.__old_shift_finished \
           or self.shift_started != self.__old_shift_started \
           or self.pause_duration != self.__old_pause_duration):
               self.shift_duration = (self.shift_finished -
               self.shift_started) - self.pause_duration
        # Lets check if this shift did not exists before and was just added from the shell!
        elif self.pk is None and self.shift_finished is not None:
            self.shift_duration = (self.shift_finished -
            self.shift_started) - self.pause_duration
        return super(Shift, self).save(*args, **kwargs)

    def shift_time_validation(self):
        """
        Validation method to check for different cases of shift overlaps
        and other violations.
        """
        errors = {}
        if self.shift_started and self.shift_finished:
            if self.shift_started > timezone.now():
                errors['shift_started'] = _('Your shift must not start in the \
                    future!')
            if self.shift_finished > timezone.now():
                errors['shift_finished'] = _('Your shift must not finish in \
                    the future!')
            if self.shift_finished < self.shift_started:
                errors['shift_finished'] = _('A shift must not finish, before \
                    it has even started!')

            # if (self.shift_finished - self.shift_started) > \
            # timedelta(hours=6):
            #    errors['shift_finished'] = _('Your shift may not be \
            # longer than 6 hours.')

            if errors:
                raise ValidationError(errors)

    def total_pause_time(self):
        """
        Returns the total pause time of the shift.
        """
        if self.pause_started:
            return (timezone.now() - self.pause_started) + self.pause_duration
        return self.pause_duration

    def is_shift_currently_paused(self):
        """
        Returns a bool value whether the current shift is paused.
        """
        return bool(self.pause_started)
    is_shift_currently_paused.boolean = True
    is_shift_currently_paused.short_description = _("Shift currently paused?")

    @property
    def is_finished(self):
        """
        Determine if there is an active shift.
        """
        return bool(self.shift_finished)

    @property
    def is_paused(self):
        """
        Return if the shift is paused or not.
        """
        return bool(self.pause_started)

    def pause(self):
        """
        Pause shift if it's not already paused.
        """
        if not self.is_paused:
            self.pause_started = timezone.now()

    def unpause(self):
        """
        Unpause shift, if it's currently paused.
        """
        if self.is_paused:
            pause_duration = timezone.now() - self.pause_started
            self.pause_duration += pause_duration
            self.pause_started = None

    def toggle_pause(self):
        """
        Toggles pause/resume to the current shift.
        """
        if self.is_paused:
            self.unpause()
        else:
            self.pause()
