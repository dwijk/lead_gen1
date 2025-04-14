from django.contrib import admin
from .models import DataStore, LeadgenData, UserData, TokenDate, UserLeadInfo, UserFieldAccess
from django import forms



# Register your models here.
admin.site.register(DataStore)
# admin.site.register(UserData)
admin.site.register(TokenDate)



@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        # Default list
        fields_to_check = ["uuid","app_id","app_secret_key"]
        selected_fields = []

        # Check if fields are set to True in the first student record
        lead = LeadgenData.objects.first()
        if lead:
            for field in fields_to_check:
                show_field = getattr(lead, f"show_{field}", False)
                if show_field:
                    selected_fields.append(field)

        return selected_fields if selected_fields else  ["uuid","app_id","app_secret_key"]  # Default if empty

    # list_display = ('uuid', 'app_id', 'app_secret_key')  # Show these fields in the list view
    # search_fields = ('uuid', 'app_id')  # Add search functionality
    # list_filter = ('app_id',)  # Add filtering by app_id
    # ordering = ('-uuid',)  # Default ordering


class LeadDataAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        # Default list
        fields_to_check = ["id","lead_id","lead_data","user_uuid"]
        selected_fields = []

        # Check if fields are set to True in the first student record
        lead = LeadgenData.objects.first()
        if lead:
            for field in fields_to_check:
                show_field = getattr(lead, f"show_{field}", False)
                if show_field:
                    selected_fields.append(field)

        return selected_fields if selected_fields else ["lead_id","lead_data","user_uuid"]  # Default if empty


    list_filter = ["id", "lead_id"]


admin.site.register(LeadgenData, LeadDataAdmin)



class UserLeadInfoAdminForm(forms.ModelForm):
    class Meta:
        model = UserLeadInfo
        fields = '__all__'

class UserInfoAdmin(admin.ModelAdmin):
    form = UserLeadInfoAdminForm

    def get_fields(self, request, obj=None):
        all_fields = [f.name for f in self.model._meta.fields]

        try:
            user_data = UserData.objects.get(user=request.user)
            access = UserFieldAccess.objects.get(user=user_data)
            allowed_fields = access.allowed_fields
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            # return []
            return all_fields

    def get_list_display(self, request):
        # Use same allowed fields for list display, minus long text fields if needed
        fields = self.get_fields(request)
        # Optional: limit very long fields like 'full_name' to avoid clutter
        excluded = ['uuid']  # Keep only relevant ones
        return [f for f in fields if f not in excluded]

    def get_fieldsets(self, request, obj=None):
        fields = self.get_fields(request, obj)

        personal_info = ['full_name', 'first_name', 'last_name', 'date_of_birth', 'gender', 'marital_status', 'relationship_status']
        contact_info = ['email', 'phone_number', 'work_email', 'work_phone_number', 'city', 'state', 'province']
        job_info = ['job_title']
        id_docs = ['cpf_brazil', 'dni_argentina', 'dni_peru', 'rut_chile', 'ci_ecuador', 'rfc_mexico']

        fieldsets = []

        def add_fieldset(title, field_list):
            included = [f for f in field_list if f in fields]
            if included:
                fieldsets.append((title, {'fields': included}))

        add_fieldset('Personal Info', personal_info)
        add_fieldset('Contact Info', contact_info)
        add_fieldset('Job Info', job_info)
        add_fieldset('Identification Documents', id_docs)

        remaining = [f for f in fields if f not in personal_info + contact_info + job_info + id_docs]
        if remaining:
            fieldsets.append(('Other Fields', {'fields': remaining}))

        return fieldsets

admin.site.register(UserLeadInfo, UserInfoAdmin)
admin.site.register(UserFieldAccess)