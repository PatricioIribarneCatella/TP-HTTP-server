import json

class RequestParser(object):

    def __init__(self):
        pass

    # Obtains a line from the socket
    def _get_line(self, client_connection, delimeter):

        c = client_connection.recv(1)
        line = ""

        while (c.decode() != delimeter):
            line = line + c.decode()
            c = client_connection.recv(1)

        print(line)

        return line.rstrip('\r')

    # Parse a HTTP request and returns
    # (header, body)
    def parse_request(self, client_connection):

        header = {}
        body = ""

        # First line contains information about client´s request
        request_line = self._get_line(client_connection, '\n')
        (header['method'], header['path'], header['version']) = request_line.split()
        
        if (header['method'] != 'GET' and
                header['method'] != 'DELETE'):
            # Second line contains information about 'Server' (address)
            next_line = self._get_line(client_connection, '\n')
            header['host'] = next_line.split(": ")[1]
            
            # Third line contains information about 'user-agent'
            next_line = self._get_line(client_connection, '\n')
            header['user-agent'] = next_line.split(": ")[1]

            # Fourth line contains information about 'accept'
            next_line = self._get_line(client_connection, '\n')
            header['accept'] = next_line.split(": ")[1]

            # Fifth line contains information about 'content-type'
            next_line = self._get_line(client_connection, '\n')
            header['content-type'] = next_line.split(": ")[1]
            
            # Sixth line contains information about 'content-length'
            next_line = self._get_line(client_connection, '\n')
            header['content-length'] = int(next_line.split(": ")[1])
            
            # Next line contains \n separator from body
            client_connection.recv(1)
            
            # Body begining
            data = client_connection.recv(header['content-length'] + 1)
            data = data.decode().rstrip('\r\n')
            body = body.join(data)
            body = json.loads(body)
        
        return header, body

    # From a response body builds a HTTP response
    def build_response(self, res_body, status):

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

