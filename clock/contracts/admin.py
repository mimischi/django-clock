from django.contrib import admin
from clock.contracts.models import Contract


class ContractAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'employee', 'hours', )


admin.site.register(Contract, ContractAdmin)
