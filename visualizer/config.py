import json
import os
from visualizer.error import Error

class Config:

    def __init__(self):
        try:
            self.configs = {
                '0': self.load_config('config/config_0.json'),
                '1': self.load_config('config/config_1.json'),
                '1.1': self.load_config('config/config_1.1.json'),
                '2': self.load_config('config/config_2.json'),
            }
        except FileNotFoundError:
            raise Error('no config file found - aborting')

    def load_config(self, path : str) -> dict[str, str]:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            try:
                with open(path, 'r') as config_file:
                    return json.load(config_file)
            except json.JSONDecodeError:
                print('please provide a valid .json config file')
        else:
            Error('no config file found - aborting')
    
    def get_config(self, index : str) ->dict[str, str]:
        return self.configs[index]
    
