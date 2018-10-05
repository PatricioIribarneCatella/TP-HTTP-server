import os
import json
from cache import Cache

class FileManager(object):

    def __init__(self, store_dir):
        
        self.method_handler = {
            'get': self._get_handler,
            'post': self._post_handler,
            'put': self._put_handler,
            'delete': self._del_handler
        }

        self.store_dir = store_dir

    def _get_handler(self, header, body):
        
        if (self.cache.empty()):
            return {'msg': 'not found'}, '404 ERROR'

        uid = header['path'].split("/")[3]
        
        data = self.cache.get(uid)

        if (data == None):
            try:
                with open(self.store_dir + uid, "r") as f:
                    data = json.load(f)
                self.cache.put(uid, data, 1)
            except FileNotFoundError:
                return {'msg': 'not found'}, '404 ERROR'

        return data, '200 OK'

    def _post_handler(self, header, body):

        uid = header['path'].split("/")[3]

        self.cache.put(uid, body, 0)
        
        return {'id': uid}, '200 OK'

    def _put_handler(self, header, body):
        
        if (self.cache.empty()):
            return {'msg': 'not found'}, '404 ERROR'

        uid = header['path'].split("/")[3]

        if (not self.cache.update(uid, body)):
            try:
                with open(self.store_dir + uid, "r+") as f:
                    json.dump(body, f)
                self.cache.put(uid, body)
            except FileNotFoundError:
                return {'msg': 'not found'}, '404 ERROR'
        
        return {}, '200 OK'

    def _del_handler(self, header, body):

        if (self.cache.empty()):
            return {'msg': 'not found'}, '404 ERROR'

        uid = header['path'].split("/")[3]

        is_in_disc = self.cache.delete(uid)
        
        if (is_in_disc):
            try:
                os.remove(self.store_dir + uid)
            except FileNotFoundError:
                return {'msg': 'not found'}, '404 ERROR'

        return {}, '200 OK'

    def handle_request(self, req_queue, res_queues):

        quit = False

        while not quit:
            
            # (req_header, req_body, pid, address)
            req = req_queue.get()

            if (req == None):
                quit = True
                continue

            header = req[0]
            body = req[1]
            pid = req[2]
            address = req[3]

            h = self.method_handler.get(header['method'].lower())

            res_body, status = h(header, body)

            res_queues[pid].put((header, res_body, status, address))

