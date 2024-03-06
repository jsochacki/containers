#!/usr/bin/env python3

import time

import os
import sys
import logging
import subprocess
import signal

TERMINAL_COMMAND = "/usr/bin/gnome-terminal"
MERCURY_DIRECTORY = "/home/blackwell/mercury"
GOOGLE_EARTH_COMMAND = "/usr/bin/google-earth-pro"
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
        self.process_list = []
        self.log = setup_logger()
        self.terminal_command = [TERMINAL_COMMAND, "--", "bash", "-c"]
        self.manifold_sleep_time = 20.0

    def execute_command(self, command):
        result = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout:
            self.log.info("Command Output: %s", result.stdout)
        if result.stderr:
            self.log.error("Command Error: %s", result.stderr)
        return result

    def form_task_command(self, task_command, location):
        command = [f'\"cd {MERCURY_DIRECTORY} && {TASK_COMMAND} {task_command} -- {location}\"']
        print(command)
        return (self.terminal_command + command)

    def launch_simulation(self, location):
        self.process_list.clear()

        command = self.form_task_command("load", location)
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

        command = self.form_task_command("manifold-real", location)
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

        self.log.warning(f'Sleeping for {self.manifold_sleep_time} seconds to give the manifold time to start')
        time.sleep(self.manifold_sleep_time)

        command = self.form_task_command("visualizer", location)
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

        command = [GOOGLE_EARTH_COMMAND, "&"]
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

        command = self.form_task_command("simulator", location)
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

    def kill_simulation(self):
        if self.process_list:
            for process in self.process_list:
                process.send_signal(signal.SIGINT)
                time.sleep(1)
                if process.poll() is None:
                    print(process)
                    print(process.pid)
                    try:
                        process.stdin.write(b"exit\n")
                        process.stdin.flush()
                    except IOError as e:
                        print(f"IOERROR encountered: {e}")
                    finally:
                        process.wait()

    def launch_simulationt(self, location):
        self.process_list.clear()

        echo_string = [f'/usr/bin/echo \"{location}\"']
        command = ["/bin/bash", "-c"] + echo_string
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

        echo_string = [f'/usr/bin/echo \"{location}\"']
        command = ["/bin/bash", "-c"] + echo_string
        print(command)
        result = self.execute_command(command)
        self.process_list.append(result)

    def estonia_scenario(self):
        self.launch_simulationt("estonia")
        #self.launch_simulation("estonia")

    def somalian_scenario(self):
        self.launch_simulationt("somalian")
        #self.launch_simulation("somalian")

    def jersey_scenario(self):
        self.launch_simulationt("jersey")
        #self.launch_simulation("jersey")

if __name__ == "__main__":
   object = simulation()
