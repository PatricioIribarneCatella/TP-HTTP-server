import os
import json

class FileManager(object):

    def __init__(self, cache_size):
        
        self.method_handler = {
            'get': self._get_handler,
            'post': self._post_handler,
            'put': self._put_handler,
            'delete': self._del_handler
        }

        #self.cache = Cache(cache_size)

    def _get_handler(self, header, body):
        
        data = None

        uid = header['path'].split("/")[3]

        try:
            with open("/data/" + uid, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {'msg': 'not found'}, '404 ERROR'

        return data, '200 OK'

    def _post_handler(self, header, body):

        uid = header['path'].split("/")[3]
        
        with open("/data/" + uid, "w") as f:
            json.dump(body, f)
        f.close()
        
        return {'id': uid}, '200 OK'

    def _put_handler(self, header, body):
        
        uid = header['path'].split("/")[3]

        try:
            with open("/data/" + uid, "r+") as f:
                json.dump(body, f)
        except FileNotFoundError:
            return {'msg': 'not found'}, '404 ERROR'
        
        return {}, '200 OK'

    def _del_handler(self, header, body):
       
        uid = header['path'].split("/")[3]

        try:
            os.remove("/data/" + uid)
        except FileNotFoundError:
            return {'msg': 'not found'}, '404 ERROR'

        return {}, '200 OK'

    def handle_request(self, req_queue, res_queues):

        quit = False

        while not quit:
            
            # (req_header, req_body, pid, address)
            req = req_queue.get()

            print("hola3")

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

