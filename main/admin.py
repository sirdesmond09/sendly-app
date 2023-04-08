from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Message, EventPreference, LovedOneProfile])


@admin.register(SMSResponse)
class SMSResponseAdmin(admin.ModelAdmin):
    list_display =  ["service", "timestamp"]
    list_filter = ["timestamp"]