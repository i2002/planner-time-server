import asyncio
import websockets
import json
import datetime
import locale
import subprocess
import os


# Data
CONFIG = {
    'work': 3000, # time in seconds
    'break': 600,
    'ip': 'localhost',
    'port': 6789,
    'locale': 'en_US.UTF-8' # used by idle info display
}

TIMER = {
    'state': -1, # -1: not started, 0: work, 1: break
    'pause': False,
    'time': 0,
    'task': ''
}

USERS = set()
TASKS = set()


# Events
def init_state_event():
    return json.dumps({
        'type': 'init',
        'timer': TIMER,
        'tasks': [*TASKS],
        # 'time': TIMER['time']
    })


def task_add_event(name):
    return json.dumps({
        'type': 'task_add',
        'name': name
    })


def task_remove_event(name):
    return json.dumps({
        'type': 'task_remove',
        'name': name
    })


def timer_sync_event(data):
    return json.dumps({
        'type': 'timer',
        'state': TIMER['state'],
        'pause': TIMER['pause'],
        'time': data['time'],
        'info': data['info']
    })


# Connection functions
async def register(websocket):
    USERS.add(websocket)


async def unregister(websocket):
    USERS.remove(websocket)


async def notify_all(type, data):
    if(not USERS):
        return
    
    if(type == 'task_add'):
        message = task_add_event(data)
    elif(type == 'task_remove'):
        message = task_remove_event(data)
    elif(type == 'timer'):
        message = timer_sync_event(data)
    else:
        message = ''
    
    await asyncio.wait([user.send(message) for user in USERS])


# Websocket server
async def message_handler(websoket, path):
    async for message in websoket:
        # parse message
        data = json.loads(message)
        action = data['action']
        value = data['value']

        # action switch
        if(action == 'timer_start'):
            timer_start(value)
            
        elif(action == 'timer_end'):
            timer_end()

        elif(action == 'timer_toggle'):
            timer_toggle()

        elif(action == 'timer_change'):
            timer_change(value)

        elif(action == 'task_add'):
            if(not value in TASKS):
                task_add(value)
                await notify_all('task_add', value)

        elif(action == 'task_remove'):
            if(value in TASKS):
                task_remove(value)
                await notify_all('task_remove', value)
        else:
            print('Action not supported: ' + action)


async def connection(websocket, path):
    await register(websocket)

    try:
        await websocket.send(init_state_event())
        await message_handler(websocket, path)
    finally:
        await unregister(websocket)


# Timer functions
def timer_start(name):
    # start if not already started
    if(TIMER['state'] != -1):
        return

    TIMER['state'] = 0

    # setup data
    TIMER['time'] = CONFIG['work']
    TIMER['pause'] = False
    TIMER['task'] = name


def timer_end():
    TIMER['state'] = -1

    # clean data
    TIMER['time'] = 0
    TIMER['pause'] = False
    TIMER['task'] = ''


def timer_toggle():
    if(TIMER['state'] != -1):
        TIMER['pause'] = not TIMER['pause']


def timer_change(name):
    if(TIMER['state'] != -1):
        TIMER['task'] = name


# Task functions
def task_add(name):
    TASKS.add(name)


def task_remove(name):
    TASKS.remove(name)


# Timer
async def timer():
    while True:
        # Update timer
        if(TIMER['state'] != -1 and not TIMER['pause']):
            TIMER['time'] -= 1

            # Timer finished
            if(TIMER['time'] < 0):
                TIMER['state'] = int(not TIMER['state'])
                TIMER['time'] = (CONFIG['work'] if TIMER['state'] == 0 else CONFIG['break']) - 1
                subprocess.Popen(["play", os.path.dirname(os.path.realpath(__file__)) + "/deskbell.wav"])

        # Broadcast time and info
        time = get_timer_time()
        info = get_timer_info()

        await notify_all('timer', {
            'time': time,
            'info': info
        })
        await asyncio.sleep(1)


def get_timer_time():
    clock_time = datetime.datetime.now().time().isoformat('minutes')
    timer_time = datetime.timedelta(seconds=TIMER['time']).__str__()[2:]

    return clock_time if TIMER['state'] == -1 else timer_time


def get_timer_info():
    if(TIMER['state'] == -1):
        return datetime.datetime.now().strftime('%d %B %Y')
    elif(TIMER['state'] == 1):
        return 'Take a break!'
    elif(TIMER['task'] == ''):
        return 'Work'
    else:
        return TIMER['task']


# Main
async def main():
    subprocess.Popen(['play', os.path.dirname(os.path.realpath(__file__)) + '/deskbell.wav'])
    locale.setlocale(locale.LC_TIME, CONFIG['locale'])
    await websockets.serve(connection, CONFIG['ip'], CONFIG['port'])
    await timer()


# Start async
asyncio.run(main())
