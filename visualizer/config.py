import json
import os
from visualizer.error import Error

class Config:

    def __init__(self, config_path : str = 'config.json'):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> dict[str, str]:
        if os.path.exists(self.config_path) and os.path.getsize(self.config_path) > 0:
            try:
                with open(self.config_path, 'r') as config_file:
                    config = json.load(config_file)
            except json.JSONDecodeError:
                print('please provide a valid .json config file')
        else:
            Error('no config file found - aborting')
        return config
    
    def get_config(self) ->dict[str, str]:
        return self.config
