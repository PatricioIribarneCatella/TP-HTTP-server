import socket
import utils as parser

# Receives header and body
# form request
#   req_header: dictionary
#   req_body: JSON
#
# Returns: tupple
#   (res_body, status)
#
def app(req_header, req_body, num_fs):
 
    req = parser.build_request(req_header, req_body)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('http_fs_1', 9999))
    s.sendall(req.encode())

    h, body = parser.parse_response(s)

    s.close()

    return body, h['status']

