# Generated by Django 4.2.18 on 2025-04-17 13:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_userfieldaccess_allowed_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='user_uuid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.userdata'),
        ),
        migrations.AddField(
            model_name='adset',
            name='user_uuid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.userdata'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='user_uuid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.userdata'),
        ),
        migrations.AlterField(
            model_name='userleadinfo',
            name='user_uuid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.userdata'),
        ),
    ]
