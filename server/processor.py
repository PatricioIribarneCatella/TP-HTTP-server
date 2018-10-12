import sys
import uuid
from os import path

from fsmanager import FileServerManager

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.responses as res

class HttpProcessor(object):

    def __init__(self, num_fs, url_fs, cache):

        self.cache = cache
        self.fs = FileServerManager(num_fs, url_fs)
        
        # Verb request handlers
        self.handlers = {
            'get': self._get_handler,
            'post': self._post_handler,
            'put': self._put_handler,
            'delete': self._del_handler
        }

    def _get_item_id(self, path, method):

        uid = ""

        if method in ["GET", "PUT", "DELETE"]:

            s = path.split("/")

            if (len(s) < 4):
                return "", "does not contain id"

            uid = s[3]
        else:
            uid = str(uuid.uuid4())

        return uid, None


    def _store_item(self, uid, data, in_disc):

        response, status = self.cache.put(uid, body, in_disc)

        if (status == res.CACHE_FULL_STATUS or
                status == res.CACHE_ZERO_SIZE_STATUS):
            self.fs.post(response["uid"],
                                response["data"])

    def _get_handler(self, header, body):

        uid, error = self._get_item_id(header["path"],
                                       header["method"])

        if (error != None):
            return res.buid_id_error(error)

        data, status = self.cache.get(uid)

        if (status == res.NOT_FOUND_STATUS):

            data, status = self.fs.get(uid)
    
            if (status == res.NOT_FOUND_STATUS):
                return data, status
            
            # the 'in_disc' flag is set to 1 because the
            # data was obtained from disc
            response, status = self.cache.put(uid, data, 1)

            # cache is full, have to back up the LRU item
            if (status == res.CACHE_FULL_STATUS):
                response, status = self.fs.post(response["uid"],
                                                response["data"])

            # but if the cache is zero size the item is
            # already in disc
            if (status == res.CACHE_ZERO_SIZE_STATUS):
                status = res.OK_STATUS

        return data, status

    def _post_handler(self, header, body):

        uid, error = self._get_item_id(header["path"],
                                       header["method"])

        if (error != None):
            return res.buid_id_error(error)

        response, status = self.cache.put(uid, body, 0)

        if (status == res.CACHE_FULL_STATUS or
                status == res.CACHE_ZERO_SIZE_STATUS):
            return self.fs.post(response["uid"],
                                response["data"])

        return res.build_successful({'id': uid})

    def _put_handler(self, header, body):

        uid, error = self._get_item_id(header["path"],
                                       header["method"])

        if (error != None):
            return res.buid_id_error(error)

        response, status = self.cache.update(uid, body)

        # cache is zero size, then directly
        # store the new data, it could return an 
        # error message if there were no such file
        if (status == res.CACHE_ZERO_SIZE_STATUS):
            return self.fs.put(uid, body)

        # the item was not in the cache
        if (status == res.NOT_FOUND_STATUS):

            if not self.fs.check(uid):
                return res.build_not_found_error()

            # store the update of the item with
            # the flag 'in_disc' turn on because
            # there is a copy of it in disc
            self._store_item(uid, body, 1)

        return res.build_successful({})

    def _del_handler(self, header, body):

        uid, error = self._get_item_id(header["path"],
                                       header["method"])

        if (error != None):
            return res.buid_id_error(error)

        response, status = self.cache.delete(uid)

        # if the entry it's backed up in disc
        # or if the entry was not there,
        # have to check in FileServer
        if (status == res.IN_DISC_STATUS or
                status == res.NOT_FOUND_STATUS):
            response, status = self.fs.delete(uid)

        return response, status


    def _handle_request(self, header, body):

        handler = self.handlers.get(header["method"].lower())

        return handler(header, body)


    def exec_request(self, req_header, req_body):

        body, status = self._handle_request(req_header,
                                            req_body)

        return body, status

