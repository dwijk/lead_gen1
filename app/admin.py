from django.contrib import admin
from .models import DataStore, LeadgenData, UserData, TokenDate
# Register your models here.
admin.site.register(DataStore)
admin.site.register(LeadgenData)
admin.site.register(UserData)
admin.site.register(TokenDate)