# Generated by Django 4.0.4 on 2022-06-23 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0004_member_member_operation_mmeber_calendar'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Mmeber_Calendar',
            new_name='MemberCalendar',
        ),
    ]
