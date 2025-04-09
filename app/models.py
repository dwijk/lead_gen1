from django.db import models
import uuid

# Create your models here.
class DataStore(models.Model):
    name = models.CharField(max_length=255)
    data = models.JSONField()



class LeadgenData(models.Model):
    lead_id = models.CharField(max_length=50, unique=True)
    user_uuid = models.ForeignKey('UserData', on_delete=models.CASCADE, to_field='uuid')
    lead_data = models.JSONField() 


class UserData(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    app_id = models.CharField(max_length=100,blank=True, null=True)
    app_secret_key = models.CharField(max_length=100,blank=True, null=True)
    
    def __str__(self):
        return f"UserData UUID: {self.uuid}"

class TokenDate(models.Model):
    user_uuid = models.ForeignKey('UserData', on_delete=models.CASCADE, to_field='uuid')
    short_time_access_token = models.CharField(max_length=512, unique=True)
    long_time_access_token = models.CharField(max_length=512, unique=True)
    short_token_created_date = models.DateField()
    long_token_created_date = models.DateField()

    def __str__(self):
        return f"Short Token: {self.short_time_access_token[:10]}... | Long Token: {self.long_time_access_token[:10]}..."