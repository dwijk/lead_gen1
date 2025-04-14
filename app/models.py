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



class LeadgenData(models.Model):
    lead_id = models.CharField(max_length=50, unique=True)
    user_uuid = models.ForeignKey(UserData, on_delete=models.CASCADE)
    lead_data = models.JSONField()
    



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