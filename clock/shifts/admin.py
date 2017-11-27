from django.contrib import admin

from clock.shifts.models import Shift


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('employee', 'contract', 'shift_started', 'shift_finished',
                    'shift_duration', 'pause_duration',
                    'is_shift_currently_paused', 'created_at')


admin.site.register(Shift, ShiftAdmin)
