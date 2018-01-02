from django.contrib import admin

from clock.shifts.models import Shift


class ShiftAdmin(admin.ModelAdmin):
    list_display = ('employee', 'contract', 'started', 'finished', 'duration',
                    'created_at')


admin.site.register(Shift, ShiftAdmin)
