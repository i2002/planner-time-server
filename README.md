# Planner time server

## About
Planner is a simple centralized time management tool.
It combines the [Pomodoro technique](https://en.wikipedia.org/wiki/Pomodoro_Technique) and a simple Todo list.

It works by having clients connect to a time server via websockets.
This project represents the **server** part of the application.

- A gnome GUI **client** can be found [here](https://gitlab.com/i2002/planner-gnome-client).
- A Cinnamon applet **client** can be found [here](https://gitlab.com/i2002/planner-cinnamon-applet)

## Installation
### Requirements
- `python 3`
- `websockets` python module

### Config
In the config file `config.json` (create one using `cp config-example.json config.json`)
- websocket IP and port (set up according to your environment)
- the work and break duration
- the locale for timer idle info

### Running
- `python <path-to-project>/planner.py`

## Connection details
### Sent messages
- `init` - timer state and tasks
- `timer` - sends to clients JSON objects with current state, pause state, time and info
- `task_add` - name of the added task
- `task_remove` - name of the removed task

### Received messages
*(JSON serialized object with `action` and `value` attributes)*

| `action` | `value` | Effect |
| -------- | ------- | ------ |
| `timer_start` | string representing the name of the active task / empty string if none | starts the pomodoro timer |
| `timer_end` | *empty string* | ends the pomodoro timer |
| `timer_toggle` | *empty string* | pauses / resumes the pomodoro timer |
| `timer_change` | string representing the name of the new task | changes active task if timer running |
| `task_add` | string representing the name of the added task | adds a new task |
| `task_remove` | string representing the name of the removed task | removes a task |
