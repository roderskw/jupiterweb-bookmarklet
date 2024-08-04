from icalendar import Calendar, Event , Timezone, TimezoneStandard
import json

import datetime
from datetime import datetime, timedelta
import pytz

import uuid

def convert_date_and_time(date : str, time = "00:00"):
    if (len(date) < 10 or len(time) < 5):
        return None
    
    d = date.split("/")
    dd = int(d[0])
    mm = int(d[1])
    yyyy = int(d[2])
    t = time.split(":")
    hh = int(t[0])
    m = int(t[1])

    return datetime(yyyy, mm, dd, hh, m, 0, tzinfo=pytz.timezone("America/Sao_Paulo"))

def get_weekdays_in_interval(weekday : int, start_date : datetime, end_date : datetime):
    if(weekday < 0 and weekday > 6):
        print("Data da semana invalida")
        return 0

    delta_date = start_date
    weekdays = []

    while delta_date <= end_date:
        if(delta_date.weekday() == weekday):
            break
        else:
            delta_date += timedelta(days=1)

    while delta_date <= end_date:
        weekdays.append(delta_date)
        delta_date += timedelta(days=7)

    return weekdays

def convert_time_to_int(time : str):
    return list(map(int, time.split(':')))

def add_event(cal, data : dict):
    event_dates = get_weekdays_in_interval(data['weekday'], convert_date_and_time(data['start_date']),  convert_date_and_time(data['end_date']))

    for i in range(len(event_dates)):    
        start = event_dates[i] + timedelta(hours=convert_time_to_int(data['start'])[0], minutes=convert_time_to_int(data['start'])[1]) #set start time
        end = event_dates[i] + timedelta(hours=convert_time_to_int(data['end'])[0], minutes=convert_time_to_int(data['end'])[1])       #set end time

        e = Event()
        e.add('uid', uuid.uuid4().hex)
        e.add('dtstamp', datetime.now())
        e.add('summary', data['code'].split('-')[0] + " - " + data['name'])
        e.add('dtstart', start)
        e.add('dtend', end)
        e.add('description', data['prof'])

        cal.add_component(e)

    return cal

def add_parameter(parameter : str, value : str, event_summary : str, cal):
    try:
        for x in cal.walk("VEVENT"):
            if(x['summary'] == event_summary):
                x.add(parameter, value)
        print("Parameter " + parameter + " was sucessfully added to " + event_summary + "!")
        return 0
    except:
        print("Any event with this summary was found!")
        return 1

def edit_parameter(parameter : str, new_value : str, event_summary : str, cal):
    try:
        for x in cal.walk("VEVENT"):
            if(x['summary'] == event_summary and x[parameter]):
                x[parameter] = new_value
        print("Parameter " + parameter + " was sucessfully changed to " + new_value + "!")
        return 0
    except Exception as e:
        print("Parameter to be edited was not found!")
        print(e)
        return 1

def list_summary(cal):
    events = []
    for x in cal.walk("VEVENT"):
        events.append(x['summary'])

    return set(events)

def list_parameters(cal, event_summary):
    parameters = []
    for x in cal.walk("VEVENT"):
        if(x['summary'] == event_summary):
            for y in x.content_lines():
                parameters.append(y.split(':')[0])
    return set(parameters)


def open_cal(file):
    input = open(file, "r", encoding="utf-8") #enconding to get all special characters
    data = Calendar.from_ical(input.read())
    input.close()
    return data

def open_data(file):
    input = open(file, "r", encoding="utf-8") #enconding to get all special characters
    data = json.loads(input.read())
    input.close()
    return data

def write_cal(cal):
    f = open("calendar.ics", 'wb')
    f.write(cal.to_ical())
    f.close()

#weekday 0  is monday

#1 - open existing cal
    #select cal
    #11 - edit parameter
        #111 - which events edit parameter (by summary) #check
        #112 - back
    #12 - add parameter
        #121 - which events add parameter (by summary) #check
        #122 - back
    #13 - back
#2 - create cal from data
#3 - close

def edit_parameter_page(cal):
    summaries = list(list_summary(cal))
    print("Unique summaries in this calendar")
    for x in range(len(summaries)):
        print(str(x) + " -> " + str(summaries[x]))
    
    index_summary = input("Summary of events to be edited:\n")

    try:
        index_summary = int(index_summary)
    except:
        print("Not a valid option!")
        return 1

    parameters = list(list_parameters(cal, summaries[index_summary]))
    print("Parameters in this event")
    for x in range(len(parameters)):
        print(str(x) + " -> " + str(parameters[x]))

    index_parameter = input("Parameter to be edited:\n")

    try:
        index_parameter = int(index_parameter)
    except:
        print("Not a valid option!")
        return 1

    new_value = input("New value to be written:\n")

    e = edit_parameter(parameters[index_parameter], new_value, summaries[index_summary], cal)

    if(e == 1):
        return 1

    write_cal(cal)

    return 0

def add_parameter_page(cal):
    summaries = list(list_summary(cal))
    print("Unique summaries in this calendar")
    for x in range(len(summaries)):
        print(str(x) + " -> " + str(summaries[x]))
    
    index_summary = input("Summary of events to be edited:\n")

    try:
        index_summary = int(index_summary)
    except:
        print("Not a valid option!")
        return 1

    parameters = list(list_parameters(cal, summaries[index_summary]))
    print("Parameters in this event")
    for x in range(len(parameters)):
        print(str(x) + " -> " + str(parameters[x]))

    parameter = input("Parameter to be added:\n")
    
    new_value = input("Value of new parameter:\n")

    e = add_parameter(parameter, new_value, summaries[index_summary], cal)

    if(e == 1):
        return 1
    
    write_cal(cal)

    return 0

def create_calendar_page():
    file = input("Name of file with data:\n")

    try:
        data = open_data(file)
    except:
        print("No file found or data is not a JSON!")
        return 1
    
    if(type(data) != list):
        if(type(data) != dict):
            print("File does not contain valid data!")
            return 1
        else:
            data[0] = data

    cal = Calendar()
    cal.add('prodid', 'Calendar_made_by_a_python_script!')
    cal.add('version', '2.0')

    timezone = Timezone()
    timezone['tzid'] = "America/Sao_Paulo"

    standard = TimezoneStandard()
    standard['dtstart'] = '20240101T000000Z' 
    standard['TZOFFSETFROM'] =  '-0300'
    standard['TZOFFSETTO'] = '-0300'

    timezone.add_component(standard)
    cal.add_component(timezone)

    for x in data:
        add_event(cal, x)

    write_cal(cal)
    
    print("Calendar created and saved in calendar.ics")
    return 0

def parameter_page(data):
    print("Select an option:")
    print("      1 - Edit parameter")
    print("      2 - Create new parameter")
    print("Any key - Back")

    sel = input()

    try:
        sel = int(sel)
    except:
        return 1

    if(sel == 1):
        if(edit_parameter_page(data) == 0):
            return 1 #done and leave
        else:
            return 0 #restart
    elif(sel == 2):
        if(add_parameter_page(data) == 0):
            return 1 #done and leave
        else:
            return 0 #restart
    else:
        return 1 #leave    

def main_interface(selection = 0):
    print("Select an option:")
    print("      1 - Open existing calendar")
    print("      2 - Create calendar from data")
    print("Any key - Close")

    selection = input()
    
    try:
        selection = int(selection)
    except:
        selection = 0

    if(selection == 1):
        file = input("Name of file with calendar:\n")
        try:
            data = open_cal(file)
        except:
            print("No file found or it is not a calendar!")
            return 0
        inter2 = parameter_page(data)
        while(inter2 == 0):
            inter2 = parameter_page(data)
        return 0
    elif(selection == 2):
        if(create_calendar_page() == 0):
            return 0 #restart
        else:
            return 0
    else:
        return 1 #leave


result = 0
while(result == 0):
    result = main_interface()

#cal = Calendar()
#
#event = Event()
#event.add('name', 'Awesome Meeting')
#event.add('description', 'Define the roadmap of our awesome project')
#event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
#event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc))
#
#cal.add_component(event)

#
#for x in event.content_lines():
#    print(x.split(':')[0])
    


