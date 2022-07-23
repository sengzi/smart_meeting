from django.db import connections
from django.db import models

# Create your models here.
class Member(models.Model):   
    member_name =  models.CharField(max_length=255)
    member_password = models.CharField(max_length=255)
    member_email = models.CharField(max_length=255)
    member_phone = models.CharField(max_length=255)
    member_operation = models.CharField(max_length=255, default="")

    def __str__(self):
        return f'{self.id} - {self.member_email}'
    
    class Meta:
        db_table = "member"


class Event(models.Model):   
    event_invite_type = models.IntegerField(default=0)
    event_poll_option = models.IntegerField(default=0)
    event_title = models.CharField(max_length=255)
    event_description = models.TextField()
    event_call_method = models.IntegerField(default=0)
    event_location = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.id} - {self.event_title}'

    class Meta:
        db_table = "event"


class Event_Date(models.Model):   
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()
    result = models.IntegerField(default=0,verbose_name='Final Result')
    
    #show object id name
    def __str__(self):
        return f'{self.id}'

    class Meta:
        db_table = "event_time"


class Event_Member(models.Model):   
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)

    class Meta:
        db_table = "event_member"


class Event_Voting(models.Model):   
    eventdate_id = models.ForeignKey(Event_Date, on_delete=models.CASCADE)
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    result = models.IntegerField(default=0)
    reason = models.TextField(default="")

    class Meta:
        db_table = "event_voting"


class MemberCalendar(models.Model):   
    member_id = models.ForeignKey(Member, on_delete=models.CASCADE)
    start_time = models.CharField(max_length=255, default="")
    end_time = models.CharField(max_length=255, default="")