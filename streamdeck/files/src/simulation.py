import threading
import time

import os
import sys
import traceback
import logging
import subprocess

STOP = False

TASK_COMMAND = "/snap/bin/task"

def get_env_var(var_name):
    try:
        var = os.environ[var_name]
    except:
        sys.stderr.write(f"failed to load environment variable: \"{var_name}\"\n")
        sys.exit(-1)
    return var

def setup_logger():
    # Setup Logging
    log = logging.getLogger('streamdeck_simulator')
    formatter = logging.Formatter("[%(asctime)s] [%(name)12s] %(message)s")
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    log.addHandler(sh)
    return log

class simulation:
    def __init__(self):
        log = setup_logger()
       # Record Threads
        self.threads = []

    def execute_command(self, command):
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if result.stdout:
            self.log.info("Command Output: %s", result.stdout)
        if result.stderr:
            self.log.error("Command Error: %s", result.stderr)

    def form_load_command(self, location):
        command = [TASK_COMMAND, "load", "--", location]
        return command

    def form_hello_world_command(self, location):
        command = ["/bin/bash", "echo", "Hello world", location]
        return command

    def estonia_scenario(self):
        command = self.form_load_command("estonia")
        self.execute_command(command)

    def somalian_scenario(self):
        command = self.form_hello_world_command("somalia")
        self.execute_command(command)

    def jersey_scenario(self):
        print("this")

    def stop_simulation_threads(self):
        global STOP
        STOP = True
        for t in self.threads:
            t.join()
        STOP = False

    def _flood(self, func):
        def run():
            while True:
                global STOP
                if STOP:
                    break
                func()
                time.sleep(0.0001)

        t = threading.Thread(target=run)
        t.start()
        self.threads.append(t)

if __name__ == "__main__":
   simulation()
