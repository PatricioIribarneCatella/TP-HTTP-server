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
        self.cache = Cache(cache_size)

        super(RequestExec, self).__init__()

    def _store_item(self, uid, body, in_disc):
        # create a new entry in the cache with
        # the 'in_disc' flag
        response, status = self.cache.put(uid, body, in_disc)

        # if the cache is full or size == 0
        if (status == '601 OK' or
                status == '602 OK'):
            self.fm.post(response["uid"], response["data"])

    def _get_handler(self, header, body):
        
        uid = header['path'].split("/")[3]
        
        data, status = self.cache.get(uid)

        if (status == '404 ERROR'):

            data, status = self.fm.get(uid)

            if (status == '404 ERROR'):
                return data, status
            
            # the 'in_disc' flag is set to 1 because the 
            # item was obtained from disc
            response, status = self.cache.put(uid, data, 1)

            # cache is full, have to back up
            # the LRU item in disc
            if (status == '601 OK'):
                response, status = self.fm.post(response["uid"],
                                                response["data"])

            # but if the cache is zero size the item is
            # already in disc
            if (status == '602 OK'):
                status = '200 OK'

        return data, status

    def _post_handler(self, header, body):

        uid = header['path'].split("/")[3]

        # store the new item with the flag
        # 'in_disc' turn off because the item
        # can not be backed up yet (it's new)
        self._store_item(uid, body, 0)

        return {'id': uid}, '200 OK'

    def _put_handler(self, header, body):

        uid = header['path'].split("/")[3]

        response, status = self.cache.update(uid, body)

        # cache is zero size, then directly
        # store the new data, could return an 
        # error message if there were no such file
        if (status == '602 OK'):
            return self.fm.put(uid, body)

        # the item was not in the cache
        if (status == '404 ERROR'):

            if not self.fm.check(uid):
                return {'msg': 'not found'}, '404 ERROR'

            # store the update of the item with
            # the flag 'in_disc' turn on because
            # there is a copy of it in disc
            self._store_item(uid, body, 1)

        return {}, '200 OK'

    def _del_handler(self, header, body):

        uid = header['path'].split("/")[3]

        response, status = self.cache.delete(uid)
        
        # if the entry it's backed up in disc
        # or if the entry was not there,
        # have to check in FileManager
        if (status == '603 OK' or
                status == '404 ERROR'):
            response, status = self.fm.delete(uid)

        return response, status


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

