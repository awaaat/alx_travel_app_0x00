# Generated by Django 5.2.1 on 2025-06-02 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='property_listing',
            new_name='listing',
        ),
        migrations.AlterField(
            model_name='message',
            name='message_body',
            field=models.TextField(max_length=250),
        ),
        migrations.AlterField(
            model_name='review',
            name='comment',
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
    ]
