from django.contrib import admin
from clock.work.models import Contract, Shift
# from django.contrib.auth.forms import UserChangeForm


# class MyUserChangeForm(UserChangeForm):
#     def __init__(self, *args, **kwargs):
#         super(MyUserChangeForm, self).__init__(*args, **kwargs)
#         self.fields['email'].required = True
#         self.fields['first_name'].required = True
#         self.fields['last_name'].required = True


# class ContractInline(admin.TabularInline):
#    model = Contract
#    extra = 1


# class UserAdmin(admin.ModelAdmin):
#     form = MyUserChangeForm
#     # inlines = (ContractInline,)

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


class ContractAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'employee', 'hours',)


admin.site.register(Contract, ContractAdmin)


class ShiftAdmin(admin.ModelAdmin):
    list_display = (
                    'employee', 'contract', 'shift_started',
                    'shift_finished', 'shift_duration', 'pause_duration',
                    'is_shift_currently_paused', 'created_at')

admin.site.register(Shift, ShiftAdmin)
