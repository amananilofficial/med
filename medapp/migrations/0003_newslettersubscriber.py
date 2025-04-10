# Generated by Django 5.2 on 2025-04-08 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medapp', '0002_contactmessage_phone_number_contactmessage_whatsapp'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('whatsapp', models.BooleanField(default=False)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
