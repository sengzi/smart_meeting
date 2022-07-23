from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
import requests
import json
import random
import ast
from datetime import date, timedelta
from django.db.models import Q
from .models import Member, Event, Event_Date, Event_Member,Event_Voting,MemberCalendar
from django.http import HttpResponse
from django.template import loader
from django.utils.encoding import force_bytes
import os.path
from django.utils.safestring import SafeString
from django.middleware.csrf import get_token

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CLIENT_SECRET_FILE = '/home/sengzi/smart_meeting/meeting/credentials.json'
#CLIENT_SECRET_FILE = 'C:/Users/Seng Zi/Desktop/smart_meeting/meeting/credentials.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def main_page(request):

    return render(request, 'meeting/index.html',{

    })


def about(request):
    return render(request, 'meeting/About.html',{

    })


def contact(request):
    return render(request, 'meeting/Contact.html',{

    })

def profile(request):
    
    time_range = []
    week_dict = {}
    week = [d.isoformat() for d in get_week(datetime.datetime.now().date())]
    nor_days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    days = []
    people = []

    for i in range(datetime.datetime.now().weekday()+1,7):
        days.append(nor_days[i])
    for i in range(0,datetime.datetime.now().weekday()+1):
        days.append(nor_days[i])

    for i in range(7):
        week_dict[days[i]] = week[i]

    for i in range(24):
        num = str(i).rjust(2, '0') + ":00"
        num_half = str(i).rjust(2, '0') + ":30"
        time_range.append(num)
        time_range.append(num_half)
    
    for i in range(7):
        week_dict[days[i]] = week[i]


    member = Member.objects.filter(member_email="ongsengzi0518@gmail.com")

    if request.method =="POST":

        people = request.POST.get('invite_people', '').replace("\"","").replace("[","").replace("]","").split(",")
        
        if request.POST.get('member_id', ''):
            email = Member.objects.get(id=request.POST.get('member_id', '')).member_email

            if people[0] == "":
                people = [email]
            else:
                people.append(email)

        result = get_calendar(people, week_dict,"profile")
        result = SafeString(result).replace("\'","\"")

        return HttpResponse(SafeString(result))

    json_week = SafeString(week_dict).replace("\'","\"")

    json_time_range = json.dumps(time_range)

    if not request.session.has_key('member_id'):
        member_id = ""
        member_name = ""
        member_email = ""
        member_phone = ""
    else:
        member_id = request.session['member_id']
        member_name = request.session['member_name']
        member_email = request.session['member_email']
        member_phone = request.session['member_phone']

    # queryset = Event_Date.objects.prefetch_related('')
    return render(request, 'meeting/Profile.html',{
        "time_range" : time_range,
        "week" : week_dict,
        "json_week" : SafeString(json_week),
        "json_time_range": SafeString(json_time_range),
        "member_id" : member_id,
        "member_name" : member_name,
        "member_email" : member_email,
        "member_phone" : member_phone,
        'csrftoken': get_token(request)
    })

def group_meeting(request):

    time_range = []
    week_dict = {}
    week = [d.isoformat() for d in get_week(datetime.datetime.now().date())]
    nor_days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    days = []

    for i in range(datetime.datetime.now().weekday()+1,7):
        days.append(nor_days[i])
    for i in range(0,datetime.datetime.now().weekday()+1):
        days.append(nor_days[i])

    for i in range(24):
        num = str(i).rjust(2, '0') + ":00"
        num_half = str(i).rjust(2, '0') + ":30"
        time_range.append(num)
        time_range.append(num_half)

    for i in range(7):
        week_dict[days[i]] = week[i]

    if request.method =="POST":

        if request.POST.get('title', ''):
            people = request.POST.get('invite_people', '').replace("\"","").replace("[","").replace("]","").split(",")
            time = ast.literal_eval(request.POST.get('invite_time', ''))

            db_e = Event(
                event_title=request.POST.get('title', ''),
                event_description=request.POST.get('description', ''),
                event_location=request.POST.get('location', ''),
            )
            db_e.save()

            num = 0

            for p in people:
                create_event_member(p,db_e,request.POST.get('title', ''), request)

            for t in time:
                create_event_date(t,db_e)

        elif request.POST.get('date', ''):
            member_id = Member.objects.get(id = request.session['member_id'])
            date = ast.literal_eval(request.POST.get('date', ''))

            if request.POST.get('method', '') == "update":
                MemberCalendar.objects.filter(member_id=member_id).delete()

            for d in date:
                db_mc = MemberCalendar(
                    member_id=member_id,
                    start_time=d["start"],
                    end_time=d["end"],
                )
                db_mc.save()

        else:
            people = request.POST.get('invite_people', '').replace("\"","").replace("[","").replace("]","").split(",")
            
            if request.POST.get('member_id', ''):
                email = Member.objects.get(id=request.POST.get('member_id', '')).member_email

                if people[0] == "":
                    people = [email]
                else:
                    people.append(email)

            if request.POST.get('type', ''):
                result = get_member_calendar(people, week_dict)
            else:
                result = get_calendar(people, week_dict,"group_meeting")
                #result = recommand_date(result,week)
                result = weather_date(result,week)
            result = SafeString(result).replace("\'","\"")

            return HttpResponse(SafeString(result))

    json_week = SafeString(week_dict).replace("\'","\"")

    json_time_range = json.dumps(time_range)

    if not request.session.has_key('member_id'):
        member_id = ""
        member_name = ""
        member_email = ""
        member_phone = ""
    else:
        member_id = request.session['member_id']
        member_name = request.session['member_name']
        member_email = request.session['member_email']
        member_phone = request.session['member_phone']

    return render(request, 'meeting'+request.path+'.html',{
        "time_range" : time_range,
        "week" : week_dict,
        "json_week" : SafeString(json_week),
        "json_time_range": SafeString(json_time_range),
        "member_id" : member_id,
        "member_email" : member_email,
        'csrftoken': get_token(request)
    })

def get_week(date):

    one_day = datetime.timedelta(days=1)
    day_idx = (date.weekday() + 1) % 7  # turn sunday into 0, monday into 1, etc.
    sunday = date
    date = sunday
    for n in range(7):
        yield date
        date += one_day


def register(request):

    mydata=Member.objects.all()
    template=loader.get_template('meeting/register.html')
    message=""
    passw=[]
    maile=[]
    for x in mydata:
        passw=x.member_password
        maile=x.member_email

        if request.method =="POST":
            if request.POST.get("mail","") == maile and request.POST.get("pass","") == passw:
                request.session['status'] = "Login"
                request.session['member_id'] = x.id
                request.session['member_name'] = x.member_name
                request.session['member_email'] = x.member_email
                request.session['member_phone'] = x.member_phone

                messages.success(request, 'Signin successful')
                return render(request, 'meeting/index.html',{})
            elif request.POST.get("mail","") == maile and request.POST.get("pass","") != passw:
                message="Wrong Password"
                break
            else:
                message="Wrong Acc"

    context={
        'mymember':mydata,
        'message':message,
    }

    return HttpResponse(template.render(context,request))


def voting(request):
    #Get event id information
    event_list = Event.objects.filter(id=request.GET.get("event",""))
    latest_time_list = Event_Date.objects.filter(event_id=request.GET.get("event",""))
    member_list=Event_Member.objects.filter(event_id=request.GET.get("event",""))
    selection={}
    person=[]
    total_count=member_list.count() * latest_time_list.count()
    count=0
    template=loader.get_template('meeting/voting.html')
    #get event detail http://147.158.224.161/voting?event=9&member=61
    

    if request.method =="POST":
        reason = ""
        
        for k in request.POST.items():
            if k[0]!= 'csrfmiddlewaretoken' and k[0]!= "reason" and k[0]!= "other":
                date_id = Event_Date.objects.get(id=k[0].replace("voting_",""))
                memvber_id = Member.objects.get(id=request.GET.get("member",""))
                vote_result = k[1]
            elif k[0]== "reason" or k[0]== "other":
                if reason == "":
                    reason = k[1]
            else:
                continue

        for j in member_list:
            person=j.member_id

            if Member.objects.get(id=request.GET.get("member","")) == person: 
                Event_Voting.objects.create(eventdate_id=date_id,member_id=memvber_id,result=vote_result,reason=reason)

        for ed in latest_time_list:
            result_list=Event_Voting.objects.filter(eventdate_id=ed.id)
            count=count+result_list.count()     

        if vote_result == 0:
            result = False
        else:
            result = True 

        event_list = Event.objects.filter(id=request.GET.get("event",""))
        event_date = Event_Date.objects.filter(event_id=request.GET.get("event",""))
        event_people = Event_Member.objects.filter(event_id=request.GET.get("event",""))

        context = {
            "title": event_list[0].event_title,
            "description": event_list[0].event_description,
            "location": event_list[0].event_location,
            "date": event_date,
            "people": event_people,
            "vote_result": result
        } 

        template=loader.get_template('meeting/voting_wait.html')
        return HttpResponse(template.render(context,request))


    context = {
        'latest_time_list': latest_time_list,
        'event_list':event_list,

    }
    return HttpResponse(template.render(context,request))


def signup(request):
    template=loader.get_template('meeting/index.html')
    myda=Member.objects.all()
    mailw=[]

    for x in myda:
        mailw=x.member_email
        #show update when email exists
        if request.POST.get("Email","") == mailw and len(x.member_name)==0:
            a=request.POST.get("Text","")
            b=request.POST.get("Password","")
            d=request.POST.get("phonenumber","")
            e=request.POST.get("operation","")
            Member.objects.filter(member_email=mailw).update(member_name=a,member_password=b,member_phone=d,member_operation=e)
            return HttpResponse(template.render({},request))



    if request.method =="POST" :
        db_m = Member(
            member_name=request.POST.get("Text",""),
            member_password=request.POST.get("Password",""),
            member_email=request.POST.get("Email",""),
            member_phone=request.POST.get("phonenumber",""),
            member_operation=request.POST.get("operation","")
        )
        db_m.save()

        request.session['member_id'] = db_m.id
        return redirect('/calendar')

    return render(request, 'meeting/signup.html',{

    })


def voting_wait(request):


    return render(request, 'meeting/voting_wait.html',{

    })


def voting_done(request):
    

    return render(request, 'meeting/voting_done.html',{

    })


def logout(request):

    request.session['status'] = "Guest"

    return render(request, 'meeting/index.html',{

    })


def appointment(request):
    
    event_list = Event.objects.filter(id=request.GET.get("event",""))
    event_date = Event_Date.objects.filter(event_id=request.GET.get("event",""))
    event_people = Event_Member.objects.filter(event_id=request.GET.get("event",""))

    people = []

    for ep in event_people:
        event_voting = Event_Voting.objects.filter(Q(eventdate_id=event_date[0].id) & Q(member_id=ep.member_id))
        voting = ""

        if event_voting:
            voting = event_voting[0].result
        
        people.append({
            "member_name": ep.member_id.member_name,
            "voting": voting
        })

    return render(request, 'meeting/appoinment_details.html',{
        "title": event_list[0].event_title,
        "description": event_list[0].event_description,
        "location": event_list[0].event_location,
        "date": event_date,
        "people": people
    })


def get_calendar(people, week_dict, method):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.

    try:
    
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())


        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')

        # if not events:
        #     print('No upcoming events found.')
        #     return

        # Prints the start and name of the next 10 events

        date_event = []

        if people[0] == "":
            people = ["primary"]
        else:
            people.append("primary")

        for p in people:
            color = "%06x" % random.randint(0, 0xFFFFFF)

            events_result = service.events().list(calendarId=p, timeMin=now,maxResults=10, singleEvents=True,orderBy='startTime').execute()
            events = events_result.get('items', [])

            if p != "primary":

                member = Member.objects.filter(member_email=p)

                if member:
                    member = Member.objects.get(member_email=p)
                    member_calendar = MemberCalendar.objects.filter(member_id = member)
                    event_member = Event_Member.objects.filter(member_id = member)

                    for mc in member_calendar:
                        st = mc.start_time.split(" ")
                        et = mc.end_time.split(" ")

                        date_event.append({
                            'start': week_dict[st[0]]+" "+st[1]+":00",
                            'end': week_dict[et[0]]+" "+et[1]+":00",
                            'color': color,
                            'event': "Google Calendar"
                        })

                    for em in event_member:
                        event_date = Event_Date.objects.filter(Q(event_id=em.event_id))
                    
                        if event_date:
                            date_event.append({
                                'start': str(event_date[0].datetime_from).split("+")[0],
                                'end': str(event_date[0].datetime_to).split("+")[0],
                                'color': color,
                                'event_id': em.event_id.id,
                                'event': em.event_id.event_title
                            })

            if not events:
                continue

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date')).replace("T", " ").split("+")[0]
                end = event['end'].get('dateTime', event['end'].get('date')).replace("T", " ").split("+")[0]

                add_date = True
                start,end,add_date = check_date_same(date_event,start,end,add_date)

                if add_date:
                    date_event.append({
                        'start': start,
                        'end': end,
                        'color': color,
                        'event': "Google Calendar"
                    })

        return date_event

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []


def create_event_member(people, event_id, title, request):

    member = Member.objects.filter(member_email=people)

    if not member:

        db_m = Member(
            member_email=people,
        )
        db_m.save()

        member = db_m
    else:
        member = Member.objects.get(member_email=people)

    db_em = Event_Member(
        event_id=event_id,
        member_id=member,
    )
    db_em.save()

    email_title = "Poll for the Event: "+title+""
    email_from = "1181203438@student.mmu.edu.my"

    html_content = render_to_string("meeting/email_template.html",{
        "title":title,
        "event_id": str(event_id.id),
        "member_id": str(member.id),
        "url": request.build_absolute_uri('/')
    })

    email_message = strip_tags(html_content)
    email = EmailMultiAlternatives(email_title, email_message, email_from, [people])
    email.attach_alternative(html_content,"text/html")
    email.send()


def create_event_date(time, event_id):
    db_ed = Event_Date(
        event_id=event_id,
        datetime_from=time['start'],
        datetime_to=time['end'],
    )
    db_ed.save()


def weather_date(event,week):
    include_days = []

    city_name = "Johor Bahru"
    api_key = "4ac53b87c2233ee8de919d51d83a4347"
    exclude = "current,minutely,alerts"

    get_coord_url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'

    req = requests.get(get_coord_url).json()
    lon = req['coord']['lon']
    lat = req['coord']['lat']

    weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&exclude={exclude}&appid={api_key}'
    weather_data = requests.get(weather_url).json()

    for wd in weather_data['list']:
        if wd['weather'][0]['main'] != "Rain":
            include_days.append(datetime.datetime.fromtimestamp(int(wd['dt'])).strftime('%Y-%m-%d %H:%M:%S'))
            include_days.append(datetime.datetime.fromtimestamp(int(wd['dt'])+3600).strftime('%Y-%m-%d %H:%M:%S'))
            include_days.append(datetime.datetime.fromtimestamp(int(wd['dt'])+7200).strftime('%Y-%m-%d %H:%M:%S'))

    num = 1
    start_date = ""
    end_date = ""

    for id in include_days:

        add_date = True

        if len(include_days) > num:
            hour = int(id.split(" ")[1].split(":")[0])
            next_hour = int(include_days[num].split(" ")[1].split(":")[0])

            if (next_hour - hour) == 1 and (next_hour - hour) > 0:

                if end_date == "":
                    start_date = id

                end_date = include_days[num]

                if include_days[len(include_days)-1] == end_date:
                    start_date,end_date,add_date = check_date_same(event,start_date,end_date,add_date)

                    end_date = str(id.split(" ")[0])+" "+str(int(start_date.split(" ")[1].split(":")[0])+1).rjust(2, '0')+":"+str(id.split(" ")[1].split(":")[1])+":"+str(id.split(" ")[1].split(":")[2])
                    if add_date:
                        event.append({
                            'start': start_date,
                            'end': end_date,
                            'event': "Recommend"
                        })

            else:

                if (start_date == "" or end_date == ""):
                    start_date = id
                    end_date = str(id.split(" ")[0])+" "+str(hour+1).rjust(2, '0')+":"+str(id.split(" ")[1].split(":")[1])+":"+str(id.split(" ")[1].split(":")[2])

                start_date,end_date,add_date = check_date_same(event,start_date,end_date,add_date)

                if start_date.split(" ")[1].split(":")[0] != "23" and end_date.split(" ")[1].split(":")[0] != "24" and add_date:

                    end_date = str(id.split(" ")[0])+" "+str(int(start_date.split(" ")[1].split(":")[0])+1).rjust(2, '0')+":"+str(id.split(" ")[1].split(":")[1])+":"+str(id.split(" ")[1].split(":")[2])
                    
                    if add_date:
                        event.append({
                            'start': start_date,
                            'end': end_date,
                            'event': "Recommend"
                        })

                end_date = ""

        num += 1

    return event


def check_date_same(event,start_date,end_date,add_date):
    try:
        for e in event:
            if e["event"] != "Recommend":
                
                if start_date >= e["start"] and end_date <= e["end"]:
                    add_date = False
                    break

                if start_date >= e["start"] and start_date <= e["end"]:
                    start_date = e["end"]

                if end_date >= e["start"] and end_date <= e["end"]:
                    end_date = e["start"]

                if e["start"].split(" ")[0] == start_date.split(" ")[0]:
                    if end_date > e["end"] and start_date < e["start"]:

                        ed = e["start"]
                        start_date,ed,add_date = check_date_same(event,start_date,ed,add_date)

                        if add_date:
                            event.append({
                                'start': start_date,
                                'end': ed,
                                'event': "Recommend"
                            })

                            start_date = e["end"]
                        else:
                            add_date = False
                            break

        return (start_date,end_date,add_date)

    except HttpError as error:
        print(error)
        print(e)


def get_member_calendar(people, week_dict):

    try:
        date_event = []

        for p in people:
            color = "%06x" % random.randint(0, 0xFFFFFF)

            member = Member.objects.filter(member_email=p)

            if member:
                member = Member.objects.get(member_email=p)
                member_calendar = MemberCalendar.objects.filter(member_id = member)

                for mc in member_calendar:
                    st = mc.start_time.split(" ")
                    et = mc.end_time.split(" ")

                    date_event.append({
                        'start': week_dict[st[0]]+" "+st[1]+":00",
                        'end': week_dict[et[0]]+" "+et[1]+":00",
                        'color': color,
                        'event': ""
                    })
                    
        return date_event

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []


# def recommand_date(result,week):
    
#     for w in week:
#         for x in range(23):
#             if x % 5 == 0:
#                 y = x+1
#                 start_date = w+" "+str(x).rjust(2, '0')+":00:00"
#                 end_date = w+" "+str(y).rjust(2, '0')+":00:00"
#                 add_date = True

#                 start_date,end_date,add_date = check_date_same(result,start_date,end_date,add_date)

#                 if add_date:
#                     result.append({
#                         'start': start_date,
#                         'end': end_date,
#                         'event': "Recommend"
#                     })
    
#     return result
