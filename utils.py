import json

# Obtains a line from the socket
def _get_line(client_connection, delimeter):

    c = client_connection.recv(1)
    line = ""

    while (c.decode() != delimeter):
        line = line + c.decode()
        c = client_connection.recv(1)

    print(line)

    return line.rstrip('\r')

# Parse a HTTP request and returns
# (header, body)
def parse_request(client_connection):

    header = {}
    body = ""

    # First line contains information about client´s request
    line = _get_line(client_connection, '\n')
    (header['method'], header['path'], header['version']) = line.split()
    
    if (header['method'] != 'GET' and
            header['method'] != 'DELETE'):

        while (line != ""):
            
            line = _get_line(client_connection, '\n')

            field = line.split(": ")

            if (field[0] == 'Content-Type'):
                header['content-type'] = field[1]

            if (field[0] == 'Content-Length'):
                header['content-length'] = int(field[1])

        # Body begining
        data = client_connection.recv(header['content-length'] + 1)
        data = data.decode().rstrip('\r\n')
        body = body.join(data)
        body = json.loads(body)
    
    return header, body


# Parse a HTTP response
# (header, body)
def parse_response(connection):

    header = {}
    body = ""

    # First line contains information about server´s response
    line = _get_line(connection, '\n')
    (header['version'], header['status'], header['status-name']) = line.split()

    while (line != ""):
        
        line = _get_line(client_connection, '\n')

        field = line.split(": ")

        if (field[0] == 'Content-Type'):
            header['content-type'] = field[1]

        if (field[0] == 'Content-Length'):
            header['content-length'] = int(field[1])

    # Body begining
    data = client_connection.recv(header['content-length'] + 1)
    data = data.decode().rstrip('\r\n')
    body = body.join(data)
    body = json.loads(body)
    
    return header, body


# From a response body builds a HTTP response
def build_response(res_body, status):

    body = json.dumps(res_body,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))

    json_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', len(body))
    ]

    response = 'HTTP/1.1 {status}\n'.format(status=status)

    for h in json_headers:
        response += '{0}: {1}\n'.format(h[0], h[1])

    response += '\n'
    response += body

    return response

# From header and body builds a HTTP request
def build_request(header, req_body):

    body = json.dumps(res_body,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))

    json_headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', len(body))
    ]

    request = '{method} {path} {http}\n'.format(
                    method=header['method'],
                    path=header['path'],
                    http=header['version'])

    for h in json_headers:
        request += '{0}: {1}\n'.format(h[0], h[1])

    response += '\n'
    response += body

    return request

