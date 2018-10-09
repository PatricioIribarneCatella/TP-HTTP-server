import sys
import json
from pathlib import Path
from os import path, remove

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.responses as response

class FileManager(object):

    def __init__(self, store_dir):
        self.store_dir = store_dir

    def get(self, uid):
        try:
            with open(self.store_dir + uid, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return response.build_not_found_error()

        return response.build_successful(data)

    def post(self, uid, data):

        with open(self.store_dir + uid, "w") as f:
            json.dump(data, f)
        
        return response.build_successful({'id': uid})

    def put(self, uid, data):
        try:
            with open(self.store_dir + uid, "r+") as f:
                json.dump(data, f)
        except FileNotFoundError:
            return response.build_not_found_error()
    
        return response.build_successful({})

    def delete(self, uid):
        try:
            remove(self.store_dir + uid)
        except FileNotFoundError:
            return response.build_not_found_error()

        return response.build_successful({})

    def check(self, uid):
        path = Path(self.store_dir + uid)
        return path.is_file()

