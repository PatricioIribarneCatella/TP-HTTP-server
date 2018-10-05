import uuid
import socket

import ..libs.parser as parser

class HttpProcessor(object):

    def __init__(self, num_fs, url_fs):
        self.num_fs = num_fs
        self.url_fs = url_fs
        
        # Verb request handlers
        self.handlers = {
            'get': self._get_handler,
            'post': self._post_handler,
            'put': self._put_handler,
            'delete': self._del_handler
        }

    def _get_handler(self, path):

        s = path.split("/")

        if (len(s) < 4):
            return "", path, "does not contain id"

        uid = s[3]

        h = hash(uid[0:8]) % self.num_fs + 1
        
        if (self.url_fs == 'localhost'):
            return self.url_fs, path, ""

        return self.url_fs + str(h), path, ""

    def _post_handler(self, path):

        uid = str(uuid.uuid4())

        h = hash(uid[0:8]) % self.num_fs + 1

        if (self.url_fs == 'localhost'):
            return self.url_fs, path + "/" + uid, ""

        return self.url_fs + str(h), path + "/" + uid, ""

    def _put_handler(self, path):

        return _get_handler(path)

    def _del_handler(self, path):
        
        return _get_handler(self, path)

    def _handle_request(self, method, path):

        handler = self.handlers.get(method.lower())

        return handler(path)

    def exec_request(self, req_header, req_body):

        body = ""
        status = ""

        fs_id, path, error = self._handle_request(req_header['method'],
                                                  req_header['path'])

        if (error != ""):
            body = {'msg': error}
            status = '405 ERROR'
        else:
            req_header['path'] = path

            req = parser.build_request(req_header, req_body)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                
                s.connect((fs_id, 9999))
                
                s.sendall(req.encode())
                
                h, body = parser.parse_response(s)
                s.close()

            except socket.error:
                return {'msg': 'internal error'}, '500 ERROR'

            status = h['status']

        return body, status

