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
        line = self._get_line(client_connection, '\n')
        (header['method'], header['path'], header['version']) = line.split()
        
        if (header['method'] != 'GET' and
                header['method'] != 'DELETE'):

            while (line != ""):
                
                line = self._get_line(client_connection, '\n')

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

