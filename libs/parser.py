import json

# Obtains a line from the socket
def _get_line(connection, delimeter):

    c = connection.recv(1)
    line = ""

    while (c.decode() != delimeter):
        line = line + c.decode()
        c = connection.recv(1)

    return line.rstrip('\r')

# Parses HTTP body
def _parse_body(connection):
    
    body = ""
    line = " "
    header = {}

    while (line != ""):
            
        line = _get_line(connection, '\n')

        field = line.split(": ")

        if (field[0] == 'Content-Type'):
            header['content-type'] = field[1]

        if (field[0] == 'Content-Length'):
            header['content-length'] = int(field[1])

    # Body begining
    data = connection.recv(header['content-length'] + 1)
    data = data.decode().rstrip('\r\n')
    body = body.join(data)
    body = json.loads(body)

    return body

# Parse a HTTP request and returns
# (header, body)
def parse_request(connection):

    header = {}
    body = ""

    # First line contains information about client´s request
    line = _get_line(connection, '\n')
    (header['method'], header['path'], header['version']) = line.split()
    
    if (header['method'] != 'GET' and
            header['method'] != 'DELETE'):
        body = _parse_body(connection)
            
    return header, body


# Parse a HTTP response
# (header, body)
def parse_response(connection):

    header = {}

    # First line contains information about server´s response
    line = _get_line(connection, '\n')
    (header['version'], header['status'], header['status-name']) = line.split()

    body = _parse_body(connection)
        
    return header, body

# Builds the http packet
def _build_http_packet(initial_header, body):

    body = json.dumps(body,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))

    json_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', len(body))
    ]

    packet = initial_header

    for h in json_headers:
        packet += '{0}: {1}\n'.format(h[0], h[1])

    packet += '\n'
    packet += body

    return packet

# From a response body builds a HTTP response
def build_response(res_body, status):

    h = 'HTTP/1.1 {status}\n'.format(status=status)

    return _build_http_packet(h, res_body) 

# From header and body builds a HTTP request
def build_request(header, req_body):

    h = '{method} {path} {http}\n'.format(
                    method=header['method'],
                    path=header['path'],
                    http=header['version'])

    return _build_http_packet(h, req_body)

