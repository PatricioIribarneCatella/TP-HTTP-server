import sys
from os import path

from cache import FileCache
from filemanager import FileManager

from multiprocessing import Process

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.responses as res

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
        self.cache = FileCache(cache_size)

        super(RequestExec, self).__init__()

    def _store_item(self, uid, body, in_disc):
        # create a new entry in the cache with
        # the 'in_disc' flag
        response, status = self.cache.put(uid, body, in_disc)

        # if the cache is full or size == 0
        if (status == res.CACHE_FULL_STATUS or
                status == res.CACHE_ZERO_SIZE_STATUS):
            self.fm.post(response["uid"], response["data"])

    def _get_handler(self, header, body):
        
        uid = header['uid']
        
        data, status = self.cache.get(uid)

        if (status == res.NOT_FOUND_STATUS):

            data, status = self.fm.get(uid)

            if (status == res.NOT_FOUND_STATUS):
                return data, status
            
            # the 'in_disc' flag is set to 1 because the 
            # item was obtained from disc
            response, status = self.cache.put(uid, data, 1)

            # cache is full, have to back up
            # the LRU item in disc
            if (status == res.CACHE_FULL_STATUS):
                response, status = self.fm.post(response["uid"],
                                                response["data"])

            # but if the cache is zero size the item is
            # already in disc
            if (status == res.CACHE_ZERO_SIZE_STATUS):
                status = res.OK_STATUS

        return data, status

    def _post_handler(self, header, body):

        uid = header['uid']

        # store the new item with the flag
        # 'in_disc' turn off because the item
        # can not be backed up yet (it's new)
        self._store_item(uid, body, 0)

        return res.build_successful({'id': uid})

    def _put_handler(self, header, body):

        uid = header['uid']

        response, status = self.cache.update(uid, body)

        # cache is zero size, then directly
        # store the new data, it could return an 
        # error message if there were no such file
        if (status == res.CACHE_ZERO_SIZE_STATUS):
            return self.fm.put(uid, body)

        # the item was not in the cache
        if (status == res.NOT_FOUND_STATUS):

            if not self.fm.check(uid):
                return res.build_not_found_error()

            # store the update of the item with
            # the flag 'in_disc' turn on because
            # there is a copy of it in disc
            self._store_item(uid, body, 1)

        return res.build_successful({})

    def _del_handler(self, header, body):

        uid = header['uid']

        response, status = self.cache.delete(uid)
        
        # if the entry it's backed up in disc
        # or if the entry was not there,
        # have to check in FileManager
        if (status == res.IN_DISC_STATUS or
                status == res.NOT_FOUND_STATUS):
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

