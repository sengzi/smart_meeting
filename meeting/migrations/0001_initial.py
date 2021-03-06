# Generated by Django 4.0.4 on 2022-05-23 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_invite_type', models.IntegerField(default=0)),
                ('event_poll_option', models.IntegerField(default=0)),
                ('event_description', models.TextField()),
                ('event_call_method', models.IntegerField(default=0)),
                ('event_location', models.CharField(max_length=100)),
                ('event_title', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'event',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_name', models.CharField(max_length=255)),
                ('member_password', models.CharField(max_length=255)),
                ('member_email', models.CharField(max_length=255)),
                ('member_phone', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'member',
            },
        ),
        migrations.CreateModel(
            name='Event_Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting.event')),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting.member')),
            ],
            options={
                'db_table': 'event_member',
            },
        ),
        migrations.CreateModel(
            name='Event_Date',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_from', models.DateTimeField()),
                ('datetime_to', models.DateTimeField()),
                ('event_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting.event')),
            ],
            options={
                'db_table': 'event_time',
            },
        ),
    ]
