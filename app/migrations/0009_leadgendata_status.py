# Generated by Django 4.2.18 on 2025-04-18 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_ad_user_uuid_adset_user_uuid_campaign_user_uuid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadgendata',
            name='status',
            field=models.CharField(blank=True, choices=[('ACTIVE', 'Active'), ('PAUSED', 'Paused'), ('DELETED', 'Deleted')], max_length=20, null=True),
        ),
    ]
