from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    app_id = models.CharField(max_length=100,blank=True, null=True)
    app_secret_key = models.CharField(max_length=100,blank=True, null=True)
    
    def __str__(self):
        return f"{self.uuid}"
    
    class Meta:
        verbose_name_plural = "User Data"
    

class DataStore(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    user_uuid = models.ForeignKey(UserData, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserLeadInfo(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_uuid = models.ForeignKey(UserData, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20,null=True,blank=True)
    whatsapp_number = models.CharField(max_length=20,null=True,blank=True)
    street_address = models.CharField(max_length=100,null=True,blank=True)
    city = models.CharField(max_length=50,null=True,blank=True)
    state = models.CharField(max_length=50,null=True,blank=True)
    country = models.CharField(max_length=50,null=True,blank=True)
    province = models.CharField(max_length=100,null=True,blank=True)
    post_code = models.CharField(max_length=20,null=True,blank=True)
    zip_code = models.CharField(max_length=20,null=True,blank=True)
    full_name = models.CharField(max_length=200,null=True,blank=True)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    date_of_birth = models.CharField(null=True,blank=True)
    gender = models.CharField(max_length=10,null=True,blank=True)
    marital_status = models.CharField(max_length=50,null=True,blank=True)
    relationship_status = models.CharField(max_length=50,null=True,blank=True)
    military_status = models.CharField(max_length=50,null=True,blank=True)
    job_title = models.CharField(max_length=50,null=True,blank=True)
    work_phone_number = models.CharField(max_length=50,null=True,blank=True)
    work_email = models.EmailField(null=True,blank=True)
    company_name = models.CharField(max_length=150,null=True,blank=True)
    cpf_brazil = models.CharField(max_length=50,null=True,blank=True)
    dni_argentina = models.CharField(max_length=50,null=True,blank=True)
    dni_peru = models.CharField(max_length=50,null=True,blank=True)
    rut_chile = models.CharField(max_length=50,null=True,blank=True)
    ci_ecuador = models.CharField(max_length=50,null=True,blank=True)
    rfc_mexico = models.CharField(max_length=50,null=True,blank=True)



class TokenDate(models.Model):
    user_uuid = models.ForeignKey(UserData, on_delete=models.CASCADE)
    short_time_access_token = models.CharField(max_length=512, unique=True)
    long_time_access_token = models.CharField(max_length=512, unique=True)
    short_token_created_date = models.DateField()
    long_token_created_date = models.DateField()

    def __str__(self):
        return f"Short Token: {self.short_time_access_token[:10]}... | Long Token: {self.long_time_access_token[:10]}..."
    


class UserFieldAccess(models.Model):
    user = models.OneToOneField(UserData, on_delete=models.CASCADE)
    allowed_fields = models.JSONField(default=list)  # List of field names

    # def __str__(self):
    #     return f"{self.user} Field Access"



class Campaign(models.Model):
    # Campaign data based on the API response
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign_id = models.CharField(max_length=50, unique=True,null=True, blank=True)
    name = models.CharField(max_length=200)
    effective_status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('DELETED', 'Deleted'),
    ])
    objective = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    budget_remaining = models.BigIntegerField(null=True, blank=True)
    daily_budget = models.BigIntegerField(null=True, blank=True)
    lifetime_budget = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Campaign: {self.name}"

class GeoLocation(models.Model):
    country = models.CharField(max_length=10 ,null=True, blank=True)

class Interest(models.Model):
    fb_id = models.CharField(max_length=50 ,null=True, blank=True)
    name = models.CharField(max_length=100 ,null=True, blank=True)

class Targeting(models.Model):
    age_min = models.IntegerField(null=True, blank=True)
    age_max = models.IntegerField(null=True, blank=True)
    genders = models.JSONField(null=True, blank=True)
    geo_locations = models.ManyToManyField(GeoLocation)
    interests = models.ManyToManyField(Interest)

class PromotedObject(models.Model):
    page_id = models.CharField(max_length=50 ,null=True, blank=True)
    custom_event_type = models.CharField(max_length=50 ,null=True, blank=True)

class AdSet(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adset_id = models.CharField(max_length=50, unique=True,null=True, blank=True)
    name = models.CharField(max_length=255 ,null=True, blank=True)
    campaign_id = models.ForeignKey(Campaign, related_name='campaign_id_campaign', on_delete=models.CASCADE,null=True, blank=True)
    account_id = models.CharField(max_length=50 ,null=True, blank=True)
    status = models.CharField(max_length=50 ,null=True, blank=True)
    daily_budget = models.CharField(max_length=20 ,null=True, blank=True)
    lifetime_budget = models.CharField(max_length=20 ,null=True, blank=True)
    budget_remaining = models.CharField(max_length=20 ,null=True, blank=True)
    bid_amount = models.CharField(max_length=20 ,null=True, blank=True)
    bid_strategy = models.CharField(max_length=100 ,null=True, blank=True)
    billing_event = models.CharField(max_length=50 ,null=True, blank=True)
    optimization_goal = models.CharField(max_length=100 ,null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    destination_type = models.CharField(max_length=50 ,null=True, blank=True)
    targeting = models.OneToOneField(Targeting, on_delete=models.CASCADE, null=True, blank=True)
    promoted_object = models.OneToOneField(PromotedObject, on_delete=models.CASCADE, null=True, blank=True)

class Ad(models.Model):
    # Ad data for a specific ad set
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ad_set = models.ForeignKey(AdSet, related_name='ad_set_adset', on_delete=models.CASCADE)
    ad_id = models.CharField(max_length=50, unique=True,null=True, blank=True)
    account_id = models.CharField(max_length=50, unique=True,null=True, blank=True)
    name = models.CharField(max_length=255 ,null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('DELETED', 'Deleted'),
    ])
    destination_set_id = models.CharField(max_length=255 ,null=True, blank=True)
    conversion_domain = models.CharField(max_length=255 ,null=True, blank=True)


    def __str__(self):
        return f"Ad: {self.name}"
    



class LeadgenData(models.Model):
    lead_id = models.CharField(max_length=50, unique=True)
    ad_id = models.ForeignKey(Ad, related_name='ad_id_ad', on_delete=models.CASCADE, null=True, blank=True)
 
    user_uuid = models.ForeignKey(UserData, on_delete=models.CASCADE)
    lead_data = models.JSONField()
    