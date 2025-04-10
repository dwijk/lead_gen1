from django.contrib import admin
from .models import DataStore, LeadgenData, UserData, TokenDate
# Register your models here.
admin.site.register(DataStore)
admin.site.register(LeadgenData)
# admin.site.register(UserData)
admin.site.register(TokenDate)



@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'app_id', 'app_secret_key')  # Show these fields in the list view
    search_fields = ('uuid', 'app_id')  # Add search functionality
    list_filter = ('app_id',)  # Add filtering by app_id
    ordering = ('-uuid',)  # Default ordering