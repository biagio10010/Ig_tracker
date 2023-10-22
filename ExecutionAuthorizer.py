import os
import json
import datetime

STATE_FILE = 'state.json'


def create_state():
    state = {'last_execution_time': str(None)}
    save_state(state)


def load_state():
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, 'r') as state_file:
            state = json.load(state_file)
            return state
    else:
        create_state()
        return load_state()


def save_state(state):
    with open(STATE_FILE, 'w') as state_file:
        json.dump(state, state_file, indent=4)


class ExecutionAuthorizer:
    def __init__(self):
        self.state = load_state()

    def authorize_execution(self):
        current_time = datetime.datetime.now()

        if self.state['last_execution_time'] != str(None):
            last_execution_time = datetime.datetime.fromisoformat(self.state['last_execution_time'])
            time_elapsed = current_time - last_execution_time

            min_elapsed_time = datetime.timedelta(minutes=2)

            if time_elapsed < min_elapsed_time:
                remaining_time = min_elapsed_time - time_elapsed
                remaining_time = str(remaining_time).split(".")[0]
                return False, remaining_time

        self.state['last_execution_time'] = str(current_time)
        save_state(self.state)
        return True, None
