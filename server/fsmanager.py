import sys
import socket
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.protocol as protocol
import utils.responses as response

class FileServerManager(object):

    def __init__(self, num_fs, url_fs):

        self.url_fs = url_fs
        self.num_fs = num_fs

    def _get_file_server_url(self, uid):
        
        h = hash(uid[0:8]) % self.num_fs + 1
        
        if (self.url_fs == 'localhost'):
            return self.url_fs

        return self.url_fs + str(h)

    def _exec_request(self, uid, body, method):

        fs_id = self._get_file_server_url(uid)

        req = protocol.encode_request(uid, method, body)
        
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

    def get(self, uid):

        return self._exec_request(uid, "", "GET")

    def post(self, uid, data):

        return self._exec_request(uid, data, "POST")

    def put(self, uid, data):

        return self._exec_request(uid, data, "PUT")

    def delete(self, uid):

        return self._exec_request(uid, "", "DELETE")


