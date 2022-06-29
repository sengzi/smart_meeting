from django.contrib import admin
from .models import *
# Register your models here.

class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_name','member_password','member_email','member_phone','member_operation')


class EventAdmin(admin.ModelAdmin):
    list_display = ('event_poll_option','event_title','event_description','event_location')


class EventDateAdmin(admin.ModelAdmin):
    list_display = ('event_id','datetime_from','datetime_to','result')
    list_filter = ('event_id',)


class EventMemberAdmin(admin.ModelAdmin):
    list_display = ('event_id','member_id')
    list_filter = ('event_id','member_id')


class EventVotingAdmin(admin.ModelAdmin):
    list_display = ('eventdate_id','member_id','result')
    list_filter = ('eventdate_id',)


class MemberCalendarAdmin(admin.ModelAdmin):
    list_display = ('member_id','start_time','end_time')
    list_filter = ('member_id',)

admin.site.register(Member, MemberAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Event_Date, EventDateAdmin)
admin.site.register(Event_Member, EventMemberAdmin)
admin.site.register(Event_Voting, EventVotingAdmin)
admin.site.register(MemberCalendar, MemberCalendarAdmin)