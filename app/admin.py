from django.contrib import admin
from .models import DataStore, LeadgenData, UserData, TokenDate, UserLeadInfo,GeoLocation, Interest, UserFieldAccess,Ad,AdSet,Campaign,Targeting,PromotedObject
from django import forms



# Register your models here.
admin.site.register(DataStore)
# admin.site.register(UserData)
admin.site.register(TokenDate)
# admin.site.register(Campaign)
admin.site.register(GeoLocation)
admin.site.register(Interest)
admin.site.register(Targeting)
admin.site.register(PromotedObject)
# admin.site.register(AdSet)
# admin.site.register(Ad)



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


class CampaignAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        all_fields = [f.name for f in self.model._meta.fields if f.editable]
        print("all_fields",all_fields)
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data",user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access",access)
            allowed_fields = access.allowed_fields
            print("allowed_fields",allowed_fields)
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_list_display(self, request):
        fields = self.get_fields(request)
        print("fields",fields)
        # excluded = ['uuid']
        # return [f for f in fields if f not in excluded]
        return fields

    def get_fieldsets(self, request, obj=None):
        fields = self.get_fields(request, obj)
        print("fields2",fields)
        basic_info = ['campaign_id', 'name', 'effective_status', 'objective']
        time_info = ['start_time', 'end_time']
        budget_info = ['budget_remaining', 'daily_budget', 'lifetime_budget']

        fieldsets = []

        def add_fieldset(title, field_list):
            included = [f for f in field_list if f in fields]
            if included:
                fieldsets.append((title, {'fields': included}))

        add_fieldset('Basic Information', basic_info)
        add_fieldset('Time Period', time_info)
        add_fieldset('Budget Information', budget_info)

        remaining = [f for f in fields if f not in basic_info + time_info + budget_info]
        if remaining:
            fieldsets.append(('Other Fields', {'fields': remaining}))

        return fieldsets


admin.site.register(Campaign, CampaignAdmin)



class AdSetAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        # Exclude non-editable fields like uuid
        all_fields = [f.name for f in self.model._meta.fields if f.editable]
        print("all_fields",all_fields)
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data",user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access",access)
            allowed_fields = access.allowed_fields
            print("allowed_fields",allowed_fields)
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_list_display(self, request):
        # Optional: include uuid in list_display even if not editable
        all_fields = [f.name for f in self.model._meta.fields]
        print("all_fields2",all_fields)

        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data2",user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access2",access)
            allowed_fields = access.allowed_fields
            print("allowed_fields2",allowed_fields)
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_fieldsets(self, request, obj=None):
        fields = self.get_fields(request, obj)
        print("fields3",fields)

        basic_info = ['adset_id', 'name', 'campaign_id', 'account_id', 'status']
        budget_info = ['daily_budget', 'lifetime_budget', 'budget_remaining', 'bid_amount', 'bid_strategy']
        optimization_info = ['billing_event', 'optimization_goal']
        time_info = ['start_time', 'end_time']
        advanced_info = ['destination_type', 'targeting', 'promoted_object']

        fieldsets = []

        def add_fieldset(title, field_list):
            included = [f for f in field_list if f in fields]
            if included:
                fieldsets.append((title, {'fields': included}))

        add_fieldset('Basic Info', basic_info)
        add_fieldset('Budget & Bidding', budget_info)
        add_fieldset('Optimization', optimization_info)
        add_fieldset('Timing', time_info)
        add_fieldset('Advanced Settings', advanced_info)

        remaining = [f for f in fields if f not in basic_info + budget_info + optimization_info + time_info + advanced_info]
        if remaining:
            fieldsets.append(('Other Fields', {'fields': remaining}))

        return fieldsets


admin.site.register(AdSet, AdSetAdmin)



class AdAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        # Exclude non-editable fields like uuid
        all_fields = [f.name for f in self.model._meta.fields if f.editable]
        print("all_fields5",all_fields)
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data5",user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access5",access)
            allowed_fields = access.allowed_fields
            print("allowed_fields5",allowed_fields)
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_list_display(self, request):
        all_fields = [f.name for f in self.model._meta.fields]
        print("all_fields4",all_fields)
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data4",user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access4",access)
            allowed_fields = access.allowed_fields
            print("allowed_fields4",allowed_fields)
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_fieldsets(self, request, obj=None):
        fields = self.get_fields(request, obj)
        print("fields4",fields)

        basic_info = ['ad_id', 'name', 'status', 'ad_set', 'account_id']
        tracking_info = ['destination_set_id', 'conversion_domain']

        fieldsets = []

        def add_fieldset(title, field_list):
            included = [f for f in field_list if f in fields]
            if included:
                fieldsets.append((title, {'fields': included}))

            print("included4",included)
        add_fieldset('Basic Info', basic_info)
        add_fieldset('Tracking Info', tracking_info)

        remaining = [f for f in fields if f not in basic_info + tracking_info]
        print("remaining4",remaining)
        if remaining:
            fieldsets.append(('Other Fields', {'fields': remaining}))

        return fieldsets


admin.site.register(Ad, AdAdmin)

