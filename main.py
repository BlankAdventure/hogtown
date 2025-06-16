# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 19:27:10 2025

@author: BlankAdventure
"""
import datetime
import asyncio
from nicegui import ui, app, ElementFilter
from model import Route, session_factory, EventRepository, EventService, Event_model
Event = tuple[Event_model, int]

site_base = '/'
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
    #ElementFilter(kind=ui.element).style('border: solid; border-width: thin; border-color: blue');
    
def format_date(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        date_obj = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return date_str

async def logout() -> None:
    '''
    Logs the user out

    Returns
    -------
    None

    '''
    app.storage.user.clear()
    ui.notify("You have been logged out.")
    await asyncio.sleep(2)    
    ui.navigate.to(site_base)

def login(username: str, password: str) -> bool:
    '''
    Checks if username and password are valid for admin login

    Parameters
    ----------
    username : str
        Username.
    password : str
        Password.

    Returns
    -------
    bool
        True/false indication if credentials are valid.
    '''
    if (username == 'admin') and (password == '12345'):
        return True
    return False
                
def is_auth() -> bool:
    '''
    Checks if current user is authorized (i.e., if logged in)

    Returns
    -------
    bool
        True/false indication if user is currently logged in.
    '''
    try:
        is_auth = app.storage.user.get('is_authenticated', False)
        return is_auth
    except AssertionError:
        return False    
    
async def login_dialog() -> None:
    '''
    Displays a dialog box for logging in.

    Returns
    -------
    None        

    '''                
    async def handle_login() -> None:
        if login(username.value, password.value):
            app.storage.user['is_authenticated'] = True
            await asyncio.sleep(2)
            ui.notify('Login successful!', color='green')
            ui.navigate.to(site_base)            
        else:
            ui.notify('Invalid credentials!', color='red')   
        dialog.close()
            
    with ui.dialog() as dialog, ui.card().classes('w-80 max-w-md mx-auto my-4'):
        ui.label('Login').classes('text-2xl mb-4')
        username = ui.input('Username').classes('w-full mb-2')
        password = ui.input('Password', password=True).classes('w-full mb-4')
        ui.button('Login', on_click=handle_login).classes('w-full bg-blue-500 text-white')    
    dialog.open()

def date_picker(in_date: str) -> ui.input:
    '''
    Creates an in-line styled date picker element.

    Parameters
    ----------
    in_date : str
        Date to show upon opening.

    Returns
    -------
    date : TYPE
        Handle to the created element.

    '''
    with ui.input('Date:', value=in_date).props('dense').classes('w-40') as date:
        with ui.menu().props('no-parent-event dense') as menu:
            with ui.date().bind_value(date):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with date.add_slot('append'):
            ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
    return date
   
def time_picker(in_time: str) -> ui.input:
    '''
    Creates an in-line styled time picker element.

    Parameters
    ----------
    in_time : str
        Time to show upon opening.

    Returns
    -------
    time : TYPE
        Handle to the created element.

    '''
    with ui.input('Time:', value=in_time).props('dense').classes('w-40') as time:
        with ui.menu().props('no-parent-event dense') as menu:
            with ui.time().bind_value(time):
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat')
        with time.add_slot('append'):
            ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
    return time
   
async def event_dialog(service: EventService, event: Event|None) -> None:
    '''
    Displays a dialog box for modifying or creating a new event.

    Parameters
    ----------
    service : EventService
        An EventService instance.
    event : Event|None
        The event to modify, or, None if creating a new event.

    Returns
    -------
    None
    '''     
    async def handle_add() -> None:
        event_dict = {'title': title.value,                     
                      'date': date.value,
                      'time': time.value,
                      'hosts': hosts.value.split(','),
                      'location': location.value,
                      'ttc': ttc.value,
                      'cost': cost.value,
                      'route': Route[route.value],
                      'comments': notes.value
                      }        
        if event:            
            if service.modify_event(event[1], event_dict):                
                ui.notify('event modified successfully!')    
                await asyncio.sleep(2)
                ui.navigate.to(site_base)
            else:
                ui.notify('Could not update event.\nYou probably entered something wrong.')
        else:
            if service.add_event(event_dict):
                ui.notify('event added successfully!')                
                await asyncio.sleep(2)
                ui.navigate.to(site_base)
            else:
                ui.notify('Could not add event.\nYou probably entered something wrong.')

    new_event = {}
    title_str = "Add New Event"
    button_str = "Add Event"
    
    if event:
        new_event = dict(event[0])
        title_str = "Edit Existing Event"
        button_str = "Update"            
    
    with ui.dialog().props('persistent')  as dialog, ui.card():
        ui.label(title_str).classes('font-bold text-lg')
        with ui.column().classes('m-0 p-0 gap-1'):
            title = ui.input('Event title:', value=new_event.get('title')).props('dense').classes('w-80')
            with ui.row():
                date = date_picker(new_event.get('date'))
                time = time_picker(new_event.get('time',"19:00"))
            hosts = ui.input('Hares (comma-separated):', value=", ".join(new_event.get('hosts',[]))).props('dense').classes('w-80')
            location = ui.input('Start location:', value=new_event.get('location')).props('dense').classes('w-80')
            with ui.row():
                ttc = ui.input('TTC:', value=new_event.get('ttc')).props('dense').classes('w-24')
                cost = ui.number('Cost:',precision=2,min=0.00,value=new_event.get('cost',10.00),format='%.2f',suffix='$',step=0.01).props('dense').classes('w-24')
                route = ui.select(label='Route:',options= {i.name: i.value for i in Route},value=new_event.get('route',Route.AA).name ).props('dense').classes('w-24')
            notes = ui.textarea('Notes:', value=new_event.get('comments')).props('dense outlined').classes('w-80 mt-4')
        with ui.row():
            ui.button(button_str, on_click=handle_add)
            ui.button('cancel', on_click=dialog.close)
    dialog.open()

def delete_dialog(service: EventService, event: Event) -> None:    
    '''
    Displays a dialog box to confirm event deletion.

    Parameters
    ----------
    service : EventService
        An EventService instance.
    event : Event
        The event to delete.

    Returns
    -------
    None

    '''
    def handle_delete() -> None:
        service.delete_event(event[1])
        ui.notify('event deleted')
        ui.navigate.to(site_base)
        
    with ui.dialog() as dialog, ui.card().classes('gap-0 items-center'):  # max-w-md mx-auto my-4       
        ui.label('Are you sure you want to delete this event?').classes('mb-2 text-lg')
        ui.label(event[0].title).classes('mb-4 font-bold text-lg')
        with ui.row():
            ui.button('HELLL YA!', on_click=handle_delete)
            ui.button('NO', on_click=dialog.close)
    dialog.open()

               
def rsvp_dialog(service: EventService, event: Event) -> None:
    '''
    Displays a dialog box for adding a name to the RSVP list.

    Parameters
    ----------
    service : EventService
        An EventService instance.
    event : Event
        The event to which the user is RSVPing.

    Returns
    -------
    None
    '''
    def add_rsvp() -> None:
        event[0].rsvp.append(name_input.value)
        service.add_rsvp(event[1], name_input.value)        
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
                for name in event[0].rsvp:
                    ui.label(name).classes('italic')
    dialog.open()
    
    
def header(service: EventService) -> None:
    '''
    Creates the page header. Available options depend on logged in/out status.

    Parameters
    ----------
    service : EventService
        An EventService instance

    Returns
    -------
    None

    '''
    with ui.header().classes('bg-blue-600 text-white items-center'):
        ui.label('The Hogtown Hash House Harriers').classes('text-2xl p-4')
        with ui.row().classes('ml-auto'):        
            ui.button('Home', on_click=lambda: ui.navigate.to(site_base)).classes('text-white')
            if is_auth():
                ui.button('New Event', on_click=lambda: event_dialog(service, None)).classes('text-white').props('color=red')
                ui.button('Logout', on_click=logout).classes('text-white')
            else:
                ui.button('Login', on_click=login_dialog).classes('text-white')
    
def event_panel(service: EventService, event: Event) -> None:    
    '''
    Creates a nice visual area for displaying event details. Includes an
    RSVP button, and if logged in, edit and delete buttons.

    Parameters
    ----------
    service : EventService
        An EventService instance.
    event : Event
        The event to display.

    Returns
    -------
    None

    '''
    def entry_line(desc,value):
        with ui.row().classes('p-0 gap-1'):
            ui.label(desc).classes('font-bold')
            ui.label(value).classes('text-gray-600')
            
    with ui.card().classes('w-2/5 p-0'): 
        with ui.row().classes('items-center w-full'):
            with ui.column().classes('p-0 gap-1 w-full'):
                with ui.row().classes('w-full items-center bg-slate-300 p-2'):
                    with ui.column().classes('p-0 gap-1'):
                        ui.label(event[0].title).classes('text-xl font-bold')
                        ui.label(f'{event[0].date.strftime(("%A %B %d, %Y"))} @ {event[0].time.strftime("%#I:%M %p")}').classes('font-bold')
                    ui.space()                    
                    ui.button("RSVP!", on_click=lambda: rsvp_dialog(service, event)).classes('justify-end')
                    if is_auth():
                        ui.button(icon='edit', on_click=lambda: event_dialog(service, event)).classes('justify-end').props('color=red')
                        ui.button(icon='delete', on_click=lambda: delete_dialog(service, event)).classes('justify-end').props('color=red')
                with ui.column().classes('p-2 gap-1'):
                    entry_line("Hares:", ", ".join(event[0].hosts))
                    entry_line('Start location:',event[0].location)
                    entry_line('TTC:',event[0].ttc)
                    entry_line('Cost:',f'${event[0].cost:.2f}')
                    entry_line('Route:',event[0].route.value)
                    entry_line('Notes from the hares:', event[0].comments)
                

def base(service: EventService) -> None:
    '''
    Top-level UI-building function. Generates the header and populates the body
    with events.

    Parameters
    ----------
    service : EventService
        An EventService instance.

    Returns
    -------
    None

    '''
    ui.query('.nicegui-content').classes('p-0')
    ui.query('body').style('background-image: url("/images/background.jpg"); background-size: cover; background-repeat: no-repeat; background-attachment: fixed; background-position: center;' )
    header(service)
    
    with ui.column().classes('w-full p-0 m-0'): 
        ui.label('About Hashing').classes('text-2xl mb-4 w-full pl-10 m-0 bg-white/70')
        ui.label(about_hasing).classes('ml-10 mr-10 text-gray-50 text-xl bg-purple-400/10 backdrop-blur-md') #bg-indigo-500/20
        ui.label('Upcoming Events').classes('text-2xl mb-4 w-full pl-10 bg-white/70')
        
        events = service.get_all_events()
        if not events:
            ui.label('No upcoming events.').classes('italic')        
        with ui.column().classes('pl-10 w-full'):
            for event in events:
                event_panel(service, event)


def add_sample_data(service: EventService) -> None:
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


def run_app_memory() -> None:
    '''
    Function for launching the app using an in-memory database (useful for testing)

    Returns
    -------
    None

    '''
    repo = EventRepository( session_factory() )
    service = EventService(repo)
    add_sample_data(service)

    @ui.page(site_base)
    def index():
        base(service)

def run_app(db_url) -> None:
    '''
    Function for launching the app using a persisted database (i.e., for production)    

    Parameters
    ----------
    db_url : TYPE
        sqlite database url.

    Returns
    -------
    None

    '''    
    repo = EventRepository( session_factory(db_url) )
    service = EventService(repo)

    @ui.page(site_base)
    def index():
        base(service)

    

        


if __name__ in {'__main__', '__mp_main__'}:
    run_app_memory()
    ui.run(storage_secret='testtest')