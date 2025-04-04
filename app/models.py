from django.db import models

# Create your models here.
class DataStore(models.Model):
    name = models.CharField(max_length=255)
    data = models.JSONField()



class LeadgenData(models.Model):
    lead_id = models.CharField(max_length=50, unique=True)
    lead_data = models.JSONField() 