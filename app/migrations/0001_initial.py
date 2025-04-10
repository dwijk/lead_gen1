# Generated by Django 4.2.18 on 2025-04-10 05:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataStore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('app_id', models.CharField(blank=True, max_length=100, null=True)),
                ('app_secret_key', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TokenDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_time_access_token', models.CharField(max_length=512, unique=True)),
                ('long_time_access_token', models.CharField(max_length=512, unique=True)),
                ('short_token_created_date', models.DateField()),
                ('long_token_created_date', models.DateField()),
                ('user_uuid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userdata')),
            ],
        ),
        migrations.CreateModel(
            name='LeadgenData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead_id', models.CharField(max_length=50, unique=True)),
                ('lead_data', models.JSONField()),
                ('user_uuid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userdata')),
            ],
        ),
    ]
