import subprocess
import requests
from requests.exceptions import Timeout
import json
import os
import logging


def wake(action, settings):
    """
    checks if kittens are awake and otherwise wakes them (i.e., starts container)
    """
    # write out action as docker-compose only accepts files
    with open("temp_workflow.json", "w") as outfile:
        outfile.write(json.dumps(action))
    for i in range(settings.n_kittens):
        if not call(f"kitten_{i}"):
            logging.info(f"Starting kitten_{i}")
            result = subprocess.run(["docker", "compose", "-f", "temp_workflow.json",
                                    "--project-name", "action",
                                    "up", "--scale", "kitten=" + str(settings.n_kittens), "-d"], 
                                    stdout=subprocess.PIPE)
            print(result.stdout.decode())
    os.remove("temp_workflow.json")
    return         


def call(name):
    """
    checks if kittens are awake and otherwise wakes them (i.e., starts contaier)
    """
    try:
        response = requests.get(name + ":5000", timeout=5)
        response.raise_for_status()
        return True
    except:
        return False

