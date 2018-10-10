import sys
import uuid
import socket
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.protocol as protocol
import utils.responses as response

class HttpProcessor(object):

    def __init__(self, num_fs, url_fs, cache):

        self.num_fs = num_fs
        self.url_fs = url_fs
        self.cache = cache
        
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
                return "", path, "does not contain id"

            uid = s[3]
        else:
            uid = str(uuid.uuid4())

        return uid

    def _get_file_server_url(self, uid, path, method):

        if (method == 'POST'):
            path = path + "/" + uid
        
        h = hash(uid[0:8]) % self.num_fs + 1
        
        if (self.url_fs == 'localhost'):
            return self.url_fs, path, ""

        return self.url_fs + str(h), path, ""

    def _request_file_server(fs_id, req_header, req_body):

        req = protocol.encode_request(req_header, req_body)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            
            s.connect((fs_id, 9999))
            
            s.sendall(req.encode())
            
            res = protocol.decode_response(s)
            s.close()

        except socket.error:
            return response.build_internal_error()

        status = res['status']
        body = res['body']

        return body, status


    def _get_handler(self, req_header, req_body):

        uid = self._get_item_id(req_header["path"],
                                req_header["method"])

        data, status = self.cache.get(uid)

        if (status == res.NOT_FOUND_STATUS):
            
            fs_id, path, error = self._get_file_server_url(req_header["path"],
                                         req_header["method"])

            req_header["path"] = path

            data, status = self._request_file_server(fs_id, req_header, req_body)
    
            if (status == res.NOT_FOUND_STATUS):
                return data, status
            
            # the 'in_disc' flag is set to 1 because the
            # data was obtained from disc
            response, status = self.cache.put(uid, data, 1)

            # cache is full, have to back up the LRU item
            if (status == res.CACHE_FULL_STATUS):
                response, status = self._request_file_server(response["uid"],
                                                response["data"])

            # but if the cache is zero size the item is
            # already in disc
            if (status == res.CACHE_ZERO_SIZE_STATUS):
                status = res.OK_STATUS

        return data, status

    def _post_handler(self, req_header, req_body):

        uid = self._get_item_id(req_header["path"],
                                req_header["method"])

        response, status = self.cache.put(uid, req_body, 0)

        if (status == res.CACHE_FULL_STATUS or
                status == res.CACHE_ZERO_SIZE_STATUS):
            self._request_file_server(response["uid"],
                        response["data"])

        return res.build_successful({'id': uid})

    def _put_handler(self, req_header, req_body):

        return res.build_successful("")

    def _del_handler(self, req_header, req_body):

        return res.build_successful("")

    def _handle_request(self, req_header, req_body):

        handler = self.handlers.get(req_header["method"].lower())

        return handler(req_header, req_body)


    def exec_request(self, req_header, req_body):

        body, status = self._handle_request(req_header,
                                            req_body)

        return body, status

