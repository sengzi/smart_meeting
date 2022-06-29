from django.shortcuts import render, redirect
from django.contrib import messages
import holidays
import datetime
import requests
import json
import random
import ast
from datetime import date, timedelta
from .models import Member, Event, Event_Date, Event_Member,Event_Voting,MemberCalendar
from django.http import HttpResponse
from django.template import loader
from django.utils.encoding import force_bytes
import os.path
from django.utils.safestring import SafeString

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CLIENT_SECRET_FILE = 'C:/Users/Seng Zi/Desktop/smart_meeting/meeting/credentials.json'
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


def group_meeting(request):

    time_range = []
    week_dict = {}
    week = [d.isoformat() for d in get_week(datetime.datetime.now().date())]
    days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]

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
                event_poll_option=request.POST.get('poll', ''), 
                event_title=request.POST.get('title', ''),
                event_description=request.POST.get('description', ''), 
                event_location=request.POST.get('location', ''),
            )
            db_e.save()
            
            num = 0

            for p in people:
                create_event_member(p,db_e)

            for t in time:
                create_event_date(t,db_e)

        elif request.POST.get('date', ''):
            member_id = Member.objects.get(id = request.session['member_id'])
            date = ast.literal_eval(request.POST.get('date', ''))
            
            for d in date:
                db_mc = MemberCalendar(
                    member_id=member_id, 
                    start_time=d["start_time"],
                    end_time=d["end_time"], 
                )
                db_mc.save()
            
        else:
            people = request.POST.get('invite_people', '').replace("\"","").replace("[","").replace("]","").split(",")
            result = get_calendar(people, week_dict)
            result = weather_date(result,week)
            result = SafeString(result).replace("\'","\"")

            return HttpResponse(SafeString(result))

    json_week = SafeString(week_dict).replace("\'","\"")

    json_time_range = json.dumps(time_range)

    return render(request, 'meeting'+request.path+'.html',{
        "time_range" : time_range,
        "week" : week_dict,
        "json_week" : SafeString(json_week),
        "json_time_range": SafeString(json_time_range)
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


def About(request):
    return render(request, 'meeting/About.html',{

    })


def voting(request):
    #Get event id information
    latest_time_list = Event_Date.objects.filter(event_id=request.GET.get("event",""))
    template=loader.get_template('meeting/voting.html')
    name_list=Event_Voting.objects.all()
    #get event detail http://147.158.224.161/voting?event=8&member=61
    # print(request.GET.get("event",""))
    # print(Event_Date.objects.filter(event_id=9))
    # time=[]
    # for x in latest_time_list:
    #     time=x.event_id
    #     count=x
        # print(time)
        # print(count)


    if request.method =="POST":
        for k in request.POST.items():
            if k[0]!='csrfmiddlewaretoken':
                if Member.objects.get(id=request.GET.get("member","")) != name_list.member_id:
                    Event_Voting.objects.create(eventdate_id=Event_Date.objects.get(id=k[0].replace("voting_","")),member_id=Member.objects.get(id=request.GET.get("member","")),result=k[1])
                else:
                    continue
  


    context = {'latest_time_list': latest_time_list,
               
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
        # db_m = Member(
        #     member_name=request.POST.get("Text",""),
        #     member_password=request.POST.get("Password",""),
        #     member_email=request.POST.get("Email",""),
        #     member_phone=request.POST.get("phonenumber",""),
        #     member_operation=request.POST.get("operation","")
        # )
        # db_m.save()
        
        # request.session['member_id'] = db_m.id
        return redirect('/calendar')

    return render(request, 'meeting/signup.html',{
    
    })


def logout(request):

    request.session['status'] = "Guest"

    return render(request, 'meeting/index.html',{
    
    })


def get_calendar(people, week_dict):
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
            # if creds and creds.expired and creds.refresh_token:
            #     creds.refresh(Request())
            # else:
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

            events_result = service.events().list(calendarId=p, timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
            events = events_result.get('items', [])
            
            
            if p != "primary":
                member = Member.objects.get(member_email=p)
                member_calendar = MemberCalendar.objects.filter(member_id = member)
            
                for mc in member_calendar:
                    st = mc.start_time.split(" ")
                    et = mc.end_time.split(" ")

                    date_event.append({
                        'start': week_dict[st[0]]+" "+st[1]+":00",
                        'end': week_dict[et[0]]+" "+et[1]+":00",
                        'color': color,
                        'event': "Google Calendar"
                    })

            if not events:
                continue

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date')).replace("T", " ").split("+")[0]
                end = event['end'].get('dateTime', event['end'].get('date')).replace("T", " ").split("+")[0]

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


def create_event_member(people, event_id):

    member = Member.objects.get(member_email=people)

    if not member:

        db_m = Member(
            member_email=people, 
        )
        db_m.save()

        member = db_m
    
    db_em = Event_Member(
        event_id=event_id, 
        member_id=member,
    )
    db_em.save()


def create_event_date(time, event_id):
    db_ed = Event_Date(
        event_id=event_id, 
        datetime_from=time['start_time'],
        datetime_to=time['end_time'],
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

    weather_url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={exclude}&appid={api_key}'
    weather_data = requests.get(weather_url).json()

    for wd in weather_data['hourly']:
        if wd['weather'][0]['main'] != "Rain":
            include_days.append(datetime.datetime.fromtimestamp(int(wd['dt'])).strftime('%Y-%m-%d %H:%M:%S'))

    num = 1
    start_date = ""
    end_date = ""

    my_holidays = holidays.country_holidays('MY')

    w_num = 0

    for w in week:
        if (w in my_holidays and w_num >2) or w == "2022-06-22":
            s = w + " 07:00:00"
            en = w + " 23:00:00"

            for e in event:
                if e["event"] == "Google Calendar" and w == e["start"].split(" ")[0]:
                    
                    if en > e["end"] and s < e["start"]:
                        event.append({
                            'start': s,
                            'end': e["start"],
                            'event': "Holiday"
                        })

                        s = e["end"]
        
            event.append({
                'start': s,
                'end': en,
                'event': "Holiday"
            })
        
        w_num += 1

    for id in include_days:

        add_date = True
        
        if len(include_days) > num:
            hour = int(id.split(" ")[1].split(":")[0])
            next_hour = int(include_days[num].split(" ")[1].split(":")[0])

            if (next_hour - hour) == 1 and (next_hour - hour) > 0:

                if end_date == "":
                    start_date = id

                end_date = include_days[num]
            else:
                
                if (start_date == "" or end_date == ""):      
                    start_date = id
                    end_date = str(id.split(" ")[0])+" "+str(hour+1).rjust(2, '0')+":"+str(id.split(" ")[1].split(":")[1])+":"+str(id.split(" ")[1].split(":")[2])

                for e in event:
                    if e["event"] == "Google Calendar":
                        
                        if start_date >= e["start"] and end_date <= e["end"]:
                            add_date = False
                            break

                        if start_date >= e["start"] and start_date <= e["end"]:
                            start_date = e["end"]
                        
                        if end_date >= e["start"] and end_date <= e["end"]:
                            end_date = e["start"]

                        if e["start"].split(" ")[0] == start_date.split(" ")[0]:
                            if end_date > e["end"] and start_date < e["start"]:
                            
                                event.append({
                                    'start': start_date,
                                    'end': e["start"],
                                    'event': "Recommend"
                                })

                                start_date = e["end"]

                if start_date.split(" ")[1].split(":")[0] != "23" and end_date.split(" ")[1].split(":")[0] != "24" and add_date:
                    event.append({
                        'start': start_date,
                        'end': end_date,
                        'event': "Recommend"
                    })

                end_date = ""

        num += 1

    return event

