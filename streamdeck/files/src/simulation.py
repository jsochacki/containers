import threading
import time

import os
import sys
import traceback
import logging

STOP = False

TASK_PATH = 

def get_env_var(var_name):
    try:
        var = os.environ[var_name]
    except:
        sys.stderr.write("failed to load environment variable: \"%s\"\n" % var_name)
        sys.exit(-1)
    return var

class simulation:
    def __init__(self):
        # Setup Logging
        log = logging.getLogger('streamdeck_simulator')
        formatter = logging.Formatter("[%(asctime)s] [%(name)12s] %(message)s")
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        log.addHandler(sh)
        # Record Threads
        self.threads = []

    def estonia_scenario(self):
        print("this")
        proc = sub
        base = "/base"
        log.info("ENVIRONMENT VARIABLES:")
        log.info("  scenario base name:      %s" % base)


    def somalian_scenario(self):
        print("this")

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
