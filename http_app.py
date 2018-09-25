import uuid
import socket
import parser

# Receives header and body
# form request
#   req_header: dictionary
#   req_body: JSON
#
# Returns: tupple
#   (res_body, status)
#

def _get_handler(path, n, url_fs):

    s = path.split("/")

    if (len(s) < 4):
        return "", path, "does not contain id"

    uid = s[3]

    h = hash(uid[0:8]) % n + 1
    
    if (url_fs == 'localhost'):
        return url_fs, path, ""

    return url_fs + str(h), path, ""

def _post_handler(path, n, url_fs):

    uid = str(uuid.uuid4())

    h = hash(uid[0:8]) % n + 1

    if (url_fs == 'localhost'):
        return url_fs, path + "/" + uid, ""

    return url_fs + str(h), path + "/" + uid, ""

def _put_handler(path, n, url_fs):

    return _get_handler(path, n, url_fs)

def _del_handler(path, n, url_fs):
    
    return _get_handler(path, n, url_fs)

# Verb request handlers
handlers = {
    'get': _get_handler,
    'post': _post_handler,
    'put': _put_handler,
    'delete': _del_handler
}

def _get_fs(method, path, num_fs, url_fs):

    h = handlers.get(method.lower())

    return h(path, num_fs, url_fs)

def app(req_header, req_body, num_fs, url_fs):

    body = ""
    status = ""

    fs_id, path, error = _get_fs(req_header['method'],
                                 req_header['path'],
                                 num_fs, url_fs)

    if (error != ""):
        body = {'msg': error}
        status = '405 ERROR'
    else:
        req_header['path'] = path

        req = parser.build_request(req_header, req_body)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      
        try:
            s.connect((fs_id, 9999))
        except socket.error:
            return {'msg': 'internal error'}, '500 ERROR'

        try:
            s.sendall(req.encode())
        except socket.error:
            return {'msg': 'internal error'}, '500 ERROR'

        try:
            h, body = parser.parse_response(s)
            s.close()
        except socket.error:
            return {'msg': 'internal error'}, '500 ERROR'

        status = h['status']

    return body, status

