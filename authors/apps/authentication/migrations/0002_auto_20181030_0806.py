# Generated by Django 2.1.2 on 2018-10-30 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='blacklistedtoken',
            unique_together=set(),
        ),
    ]