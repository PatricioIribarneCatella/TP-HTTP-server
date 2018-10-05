from cache import Cache
from filemanager import FileManager

from multiprocessing import Process

STORE_DIR = "/data/"

class RequestExec(Process):

    def __init__(self, req_queue, res_queues, cache_size):

        self.req_queue = req_queue
        self.res_queues = res_queues

        self.handlers = {
            "get": self._get_handler,
            "post": self._post_handler,
            "put": self._put_handler,
            "delete": self._del_handler
        }

        self.fm = FileManager(STORE_DIR)
        self.cache = Cache(cache_size, STORE_DIR)

        super(RequestExec, self).__init__()

    def _get_handler(self, header, body):
        
        uid = header['path'].split("/")[3]
        
        data, status = self.cache.get(uid)

        if (status == '404 ERROR'):
            data, status = self.fm.get(uid)
            self.cache.put(uid, data, 1)

        return data, status

    def _post_handler(self, header, body):

        uid = header['path'].split("/")[3]

        response, status = self.cache.put(uid, body, 0)

        # if the cache is full or size == 0
        if (status == '600 ERROR'):
            response, status = self.fm.post(uid, response)
        
        return response, status

    def _put_handler(self, header, body):

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


    def run(self):

        quit = False

        while not quit:
            
            # Remove request from queue 
            # (req_header, req_body, pid, address)
            req = self.req_queue.get()

            if (req == None):
                quit = True
                continue

            header = req[0]
            body = req[1]
            pid = req[2]
            address = req[3]
            
            handler = self.handlers.get(header['method'].lower())

            res_body, res_status = handler(header, body)

            self.res_queues[pid].put((header, res_body, res_status, address))

