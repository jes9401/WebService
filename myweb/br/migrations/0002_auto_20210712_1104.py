# Generated by Django 2.1.3 on 2021-07-12 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chek',
            old_name='date',
            new_name='start_date',
        ),
        migrations.AddField(
            model_name='chek',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
