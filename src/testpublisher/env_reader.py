import json
import os

config = {}

def load_config(path='config.json'):
    global config
    with open(os.path.join(os.getcwd(), path), 'r') as f:
        config = json.loads(f.read())

def get_var(key, default=None):
    return config.get(key) or default