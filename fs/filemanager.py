import os
import json
from cache import Cache

class FileManager(object):

    def __init__(self, store_dir):
        self.store_dir = store_dir

    def get(self, uid):
        try:
            with open(self.store_dir + uid, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {'msg': 'not found'}, '404 ERROR'

        return data, '200 OK'

    def post(self, uid, data):

        with open(self.store_dir + uid, "w") as f:
            json.dump(data, f)
        
        return {'id': uid}, '200 OK'

    def put(self, uid, data):
        try:
            with open(self.store_dir + uid, "r+") as f:
                json.dump(data, f)
        except FileNotFoundError:
            return {'msg': 'not found'}, '404 ERROR'
    
        return {}, '200 OK'

    def delete(self, uid):
        try:
            os.remove(self.store_dir + uid)
        except FileNotFoundError:
            return {'msg': 'not found'}, '404 ERROR'

        return {}, '200 OK'


