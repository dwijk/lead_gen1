from django.contrib import admin
from .models import DataStore, LeadgenData, UserData, TokenDate, UserLeadInfo,GeoLocation, Interest, UserFieldAccess,Ad,AdSet,Campaign,Targeting,PromotedObject, ListOfKeys
from django import forms



# Register your models here.



@admin.register(Targeting)
class TargetingAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(adset__user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()

@admin.register(PromotedObject)
class PromotedObjectAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(adset__user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
        

@admin.register(GeoLocation)
class GeoLocationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(targeting__adset__user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
        

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(targeting__adset__user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
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


class UserLeadInfoAdminForm(forms.ModelForm):
    class Meta:
        model = UserLeadInfo
        fields = '__all__'

class UserInfoAdmin(admin.ModelAdmin):
    form = UserLeadInfoAdminForm
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Show all data to superuser
        if request.user.is_superuser:
            return qs

        try:
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
    def get_fields(self, request, obj=None):
        all_fields = [f.name for f in self.model._meta.fields]

        try:
            user_data = UserData.objects.get(user=request.user)
            access = UserFieldAccess.objects.get(user=user_data)
            allowed_keys = list(access.allowed_fields.values_list('key', flat=True))
            return [f for f in all_fields if f in allowed_keys]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_list_display(self, request):
        fields = self.get_fields(request)
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


class CampaignAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        print("qs",qs)
        # Allow superusers to see all data
        if request.user.is_superuser:
            return qs

        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data", user_data)
            return qs.filter(user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
    def get_fields(self, request, obj=None):
        all_fields = [f.name for f in self.model._meta.fields if f.editable]
        print("all_fields", all_fields)
        
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data", user_data)
            
            access = UserFieldAccess.objects.get(user=user_data)
            print("access", access)

            # Properly extract the actual keys from the ManyToMany relationship
            allowed_fields_qs = access.allowed_fields.all()
            allowed_fields = [field.key for field in allowed_fields_qs]
            print("allowed_fields", allowed_fields)

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


class AdSetAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Superuser should see everything
        if request.user.is_superuser:
            return qs

        try:
            # Get the UserData UUID linked to the logged-in user
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
        
    def get_fields(self, request, obj=None):
    # Exclude non-editable fields like uuid
        all_fields = [f.name for f in self.model._meta.fields if f.editable]
        print("all_fields", all_fields)

        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data", user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access", access)

            # Convert the ManyRelatedManager to a list of keys
            allowed_fields = list(access.allowed_fields.values_list('key', flat=True))
            print("allowed_fields", allowed_fields)

            return [f for f in all_fields if f in allowed_fields]

        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields
    def get_list_display(self, request):
        all_fields = [f.name for f in self.model._meta.fields]

        try:
            user_data = UserData.objects.get(user=request.user)
            access = UserFieldAccess.objects.get(user=user_data)
            
            allowed_field_objs = access.allowed_fields.all()
            allowed_fields = [field.key for field in allowed_field_objs]

            # Ensure a valid identifier (e.g., uuid) is always shown
            default_field = 'uuid' if 'uuid' in all_fields else all_fields[0] if all_fields else None

            return [f for f in all_fields if f in allowed_fields] or [default_field]
        
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            default_field = 'uuid' if 'uuid' in all_fields else all_fields[0] if all_fields else None
            return [default_field]
        
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





class AdAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            user_data = UserData.objects.get(user=request.user)
            return qs.filter(user_uuid=user_data)
        except UserData.DoesNotExist:
            return qs.none()
        

    def get_fields(self, request, obj=None):
        # Exclude non-editable fields like uuid
        all_fields = [f.name for f in self.model._meta.fields if f.editable]
        print("all_fields5",all_fields)
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data5",user_data)
            access = UserFieldAccess.objects.get(user=user_data)
            print("access5",access)
            allowed_fields = list(access.allowed_fields.values_list('key', flat=True))
            print("allowed_fields5",allowed_fields)
            return [f for f in all_fields if f in allowed_fields]
        except (UserData.DoesNotExist, UserFieldAccess.DoesNotExist):
            return all_fields

    def get_list_display(self, request):
        all_fields = [f.name for f in self.model._meta.fields]
        print("all_fields4", all_fields)
        
        try:
            user_data = UserData.objects.get(user=request.user)
            print("user_data4", user_data)

            access = UserFieldAccess.objects.get(user=user_data)
            print("access4", access)

            # Get actual list of keys from related ListOfKeys objects
            allowed_fields_qs = access.allowed_fields.all()
            allowed_fields = [field.key for field in allowed_fields_qs]
            print("allowed_fields4", allowed_fields)

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




admin.site.register(DataStore)
admin.site.register(TokenDate)
admin.site.register(Ad, AdAdmin)
admin.site.register(ListOfKeys)
admin.site.register(AdSet, AdSetAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(UserLeadInfo, UserInfoAdmin)
admin.site.register(UserFieldAccess)
admin.site.register(LeadgenData, LeadDataAdmin)