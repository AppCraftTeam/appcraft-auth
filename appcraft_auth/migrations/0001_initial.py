# Generated by Django 3.2.9 on 2021-12-08 09:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthLetterModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Отправлено на')),
                ('code', models.CharField(max_length=6, verbose_name='Сгенерированный код')),
                ('key', models.CharField(default=uuid.uuid4, max_length=256, verbose_name='Защитный ключ')),
                ('trials', models.PositiveSmallIntegerField(default=0, verbose_name='Количество попыток')),
                ('last_trial_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Время последней попытки входа')),
                ('remote_ip', models.CharField(blank=True, max_length=30, null=True)),
                ('session_key', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Код авторизации по email',
                'verbose_name_plural': 'Коды авторизации по email',
                'db_table': 'appcraft_auth__auth_letters',
            },
        ),
        migrations.CreateModel(
            name='BlackListedTokenModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('access_token', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'appcraft_auth__black_listed_tokens',
            },
        ),
        migrations.CreateModel(
            name='SmsModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('phone', models.CharField(max_length=15)),
                ('code', models.CharField(max_length=8)),
                ('key', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(0, 'Sent'), (1, 'Activated'), (2, 'Canceled'), (3, 'Expired')], default=0)),
            ],
            options={
                'verbose_name': 'SMS',
                'verbose_name_plural': 'SMS',
                'db_table': 'appcraft_auth_sms_models',
            },
        ),
        migrations.CreateModel(
            name='JWTModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('access_token', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'appcraft_auth__jw_tokens',
            },
        ),
    ]
