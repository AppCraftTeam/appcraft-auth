# Generated by Django 3.2.9 on 2021-12-08 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcraft_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='smsmodel',
            table='appcraft_auth__sms_models',
        ),
        migrations.CreateModel(
            name='SocialModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('provider', models.PositiveIntegerField(blank=True, choices=[(0, 'Google'), (1, 'Apple'), (2, 'Phone'), (3, 'Facebook'), (4, 'Wechat')], null=True)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('middle_name', models.CharField(max_length=255, null=True)),
                ('username', models.CharField(max_length=255, null=True)),
                ('phone', models.CharField(max_length=255, null=True)),
                ('email', models.CharField(max_length=255, null=True)),
                ('firebase_id', models.CharField(max_length=255, null=True)),
                ('used_for_registration', models.BooleanField(default=False, verbose_name='Использовался для регистрации')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Способ авторизации пользователя',
                'verbose_name_plural': 'Способы авторизаций пользователей',
                'db_table': 'appcraft_auth__socials',
            },
        ),
    ]
