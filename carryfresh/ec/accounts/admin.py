from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account

class AcccountAdmin(UserAdmin):
    list_display=('email','first_name','last_name','username','last_login','is_active')
    filter_horizontal=()
    list_filter=()
    fieldsets=()

admin.site.register(Account,AcccountAdmin)