# Planner time server

## About
Planner is a simple centralized time management tool.
It combines the the [Pomodoro technique](https://en.wikipedia.org/wiki/Pomodoro_Technique) and a simple TO DO list.

It works by having clients connect to a time server via websockets.
This project represents the server part of the application.
A gnome GUI client can be fount [here](https://gitlab.com/i2002/planner-gnome-client)

## Installation
### Requirements:
- `python 3`
- `websockets` python module

### Config
(at the top of `planner.py` file)
- websocket IP and port (set up according to your environment)
- the work and break duration

### Running
`python <path-to-project>/planner.py`

## Connection details
** Sent messages **
- `init` timer state and tasks
- `timer` sends to clients JSON objects with current state, pause state, time and info
- `task_add` name of the added task
- `task_remove` name of the removed task

** Received messages **
(structure: `action` and `value`)
- `timer_start`, along with the name of the current task - starts the pomodoro timer
- `timer_end` - ends the pomodoro timer
- `timer_toggle` - pauses / resumes the pomodoro timer
- `timer_change`, with the name of the new task - changes active task
- `task_add`, along with the name of the added task - adds a new task
- `task_remove`, along with the name of the removed task - removes a task
