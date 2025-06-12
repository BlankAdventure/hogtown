# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 19:27:10 2025

@author: BlankAdventure
"""
import datetime
from nicegui import ui, app, ElementFilter
from model import Route, session_factory, EventRepository, EventService


repo = EventRepository( session_factory() )
service = EventService(repo)

app.add_static_files('/images', '.')

about_hasing = '''
Hogtown (aka Toronto) Hash House Harriers (H4) is a Toronto area social group 
founded in 1987 that meets regularly for events called “hashes”, where 
participants, called “hashers” work together to find and follow a trail, either 
running or walking. Typical trails are five to ten kilometers or less, 
depending on who laid the trail (called the “hare”). Anyone and everyone are 
welcome to turn up to a hash. Hashing is world-wide and there are hashes in 
many cities worldwide. A brief history and list of worldwide hashes is here .
There are no membership fees. There is typically a fee for the hash collected 
at the start, to cover the cost of a beer at the end and possibly on trail (at 
a “beer check”). First-timers pay no fee, and non-drinkers, who are regular 
participants, pay a much smaller fee to cover just the cost of laying the 
trail. Trails usually start indoors at a pub or house with a social gathering,
and the pack then heads off about 30 minutes after the “start time” to find 
and follow the trail. Then there is an optional social gathering indoors after 
the trail with food and drinks.'''

def borders_on():
    ElementFilter(kind=ui.column).style('border: solid; border-width: thin; border-color: red;');
    ElementFilter(kind=ui.row).style('border: solid; border-width: thin; border-color: green');
    ElementFilter(kind=ui.label).style('border: solid; border-width: thin; border-color: yellow');
    ElementFilter(kind=ui.element).style('border: solid; border-width: thin; border-color: blue');
    
def format_date(date_str: str):
    if not date_str:
        return ""
    try:
        date_obj = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return date_str

def logout():
    del app.storage.user['is_authenticated']    
    ui.navigate.to('/')

def login(username, password):
    if (username == 'admin') and (password == '12345'):
        return True
    return False
                
def is_auth():
    try:
        is_auth = app.storage.user.get('is_authenticated', False)
        return is_auth
    except AssertionError:
        return False    
    
def login_dialog():                
                
    def handle_login():
        if login(username.value, password.value):
            app.storage.user['is_authenticated'] = True
            ui.notify('Login successful!', color='green')
            ui.navigate.to('/')            
        else:
            ui.notify('Invalid credentials!', color='red')   
        dialog.close()

            
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-md mx-auto my-4'):
        ui.label('Login').classes('text-2xl mb-4')
        username = ui.input('Username').classes('w-full mb-2')
        password = ui.input('Password', password=True).classes('w-full mb-4')
        ui.button('Login', on_click=handle_login).classes('w-full bg-blue-500 text-white')
    
    dialog.open()


   
def new_event():
    pass

def delete_dialog(event, id):
    
    def handle_delete():
        service.delete_event(id)
        ui.notify('event deleted')
        ui.navigate.to('/')
        
    with ui.dialog() as dialog, ui.card().classes('gap-0 items-center'):  # max-w-md mx-auto my-4       
        ui.label('Are you sure you want to delete this event?').classes('mb-2 text-lg')
        ui.label(event.title).classes('mb-4 font-bold text-lg')
        with ui.row():
            ui.button('HELLL YA!', on_click=handle_delete)
            ui.button('NO', on_click=dialog.close)
    dialog.open()

@ui.refreshable                
def rsvp_dialog(event, id):
    def add_rsvp():
        event.rsvp.append(name_input.value)
        service.add_rsvp(id, name_input.value)        
        dialog.close()
        dialog.clear()
        
    with ui.dialog() as dialog, ui.card().classes('w-auto'):
        with ui.row():
            with ui.column():
                ui.label('RSVP').classes('font-bold w-full border-b')
                name_input = ui.input(label='Enter your name').props('clearable').classes('w-48')
                with ui.row():
                    ui.button('Okay', on_click=add_rsvp)
                    ui.button('Cancel', on_click=dialog.close)
            with ui.column().classes('ml-5 p-0 gap-0'):
                ui.label("Who's Cumming").classes('font-bold w-full border-b')
                for name in event.rsvp:
                    ui.label(name).classes('italic')
    dialog.open()
    
    
def header():
    with ui.header().classes('bg-blue-600 text-white items-center'):
        ui.label('The Hogtown Hash House Harriers').classes('text-2xl p-4')
        with ui.row().classes('ml-auto'):        
            ui.button('Home', on_click=lambda: ui.navigate.to('/')).classes('text-white')
            if is_auth():
                ui.button('New Event', on_click=new_event).classes('text-white').props('color=red')
                ui.button('Logout', on_click=logout).classes('text-white')
            else:
                ui.button('Login', on_click=login_dialog).classes('text-white')
    
def event_panel(in_event):
    id = in_event[1]
    event = in_event[0]

    def entry_line(desc,value):
        with ui.row().classes('p-0 gap-1'):
            ui.label(desc).classes('font-bold')
            ui.label(value).classes('text-gray-600')                

    with ui.card().classes('w-2/5 p-0'): 
        with ui.row().classes('items-center w-full'):
            with ui.column().classes('p-0 gap-1 w-full'):
                with ui.row().classes('w-full items-center bg-slate-300 p-2'):
                    with ui.column().classes('p-0 gap-1'):
                        ui.label(event.title).classes('text-xl font-bold')
                        ui.label(f'{event.date.strftime(("%A %B %d, %Y"))} @ {event.time.strftime("%#I:%M %p")}').classes('font-bold')
                    ui.space()                    
                    ui.button("RSVP!", on_click=lambda: rsvp_dialog(event, id)).classes('justify-end')
                    if is_auth():
                        ui.button(icon='edit').classes('justify-end').props('color=red')
                        ui.button(icon='delete', on_click=lambda: delete_dialog(event, id)).classes('justify-end').props('color=red')
                with ui.column().classes('p-2 gap-1'):
                    entry_line("Hares:", ", ".join(event.hosts))
                    entry_line('Start location:',event.location)
                    entry_line('TTC:',event.ttc)
                    entry_line('Cost:',f'${event.cost:.2f}')
                    entry_line('Route:',event.route.value)
                    entry_line('Notes from the hares:', event.comments)
                
@ui.page('/')
def index():
    ui.query('.nicegui-content').classes('p-0')
    ui.query('body').style('background-image: url("/images/background.jpg"); background-size: cover; background-repeat: no-repeat; background-attachment: fixed; background-position: center;' )
    header()
    
    with ui.column().classes('w-full p-0 m-0'): 
        ui.label('About Hashing').classes('text-2xl mb-4 w-full pl-10 m-0 bg-white/70')
        ui.label(about_hasing).classes('pl-10 pr-20 text-white text-xl')
        ui.label('Upcoming Events').classes('text-2xl mb-4 w-full pl-10 bg-white/70')
        
        events = service.get_all_events()
        if not events:
            ui.label('No upcoming events.').classes('italic')        
        with ui.column().classes('pl-10 w-full'):
            for event in events:
                event_panel(event)
    

def add_sample_data():
    sample_events = [
        {
            'title': 'Hogans!',
            'date': datetime.date.today() + datetime.timedelta(days=1),
            'time': datetime.time(14, 30),
            'hosts': ['Alice', 'Bob'],
            'location': 'Christie Pits Pub: 455 Bloor St East',
            'ttc': 'Christie',
            'route': Route.AA,
            'comments': 'Much drinking will be had',
            'rsvp': ['Charlie', 'Diana']
        },
        {
            'title': 'The TWAT Run!',
            'date': datetime.date.today() + datetime.timedelta(days=7),
            'time': datetime.time(12, 0),
            'hosts': ['Jessica'],
            'location': 'A Dark Horse Tavern',
            'ttc': 'Wilson',
            'cost': 15.00,
            'route': Route.AB,
            'comments': 'Bring sunscreen and comfortable shoes',
            'rsvp': []
        }
    ]
    
    for event_data in sample_events:
        service.add_event(event_data)
        
add_sample_data()

ui.run(storage_secret='testtest')