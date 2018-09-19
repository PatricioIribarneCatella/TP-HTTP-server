import sys
import socket
import argparse
import signal
from multiprocessing import Process, Queue, Event

class Server(object):

    def __init__(self, ip, port, workers, app):
       
        # Create the socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Allow to reuse the same address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind
        self.server_socket.bind((ip, port))
        
        # Listen
        self.server_socket.listen(10)

        self.server_socket.set_inheritable(True)
        
        self.ip = ip
        self.port = port
        self.app = app
        self.num_workers = workers

    def _get_line(self, client_connection, delimeter):

        c = client_connection.recv(1)
        line = ""

        while (c.decode() != delimeter):
            line = line + c.decode()
            c = client_connection.recv(1)

        print(line)

        return line.rstrip('\r')

    def _parse_request(self, client_connection):

        header = {}
        body = ""

        # First line contains information about client´s request
        request_line = self._get_line(client_connection, '\n')
        (header['method'], header['path'], header['version']) = request_line.split()
        
        if (header['method'] != 'GET' and
                header['method'] != 'DELETE'):
            # Second line contains information about 'content-type'
            next_line = self._get_line(client_connection, '\n')
            header['content-type'] = next_line.split(": ")
            # Third line contains information about 'content-length'
            next_line = self._get_line(client_connection, '\n')
            header['content-length'] = next_line.split(": ")
            # Next line contains \n separator from body
            client_connection.recv(1)
            # Body begining
            body = body.join(client_connection.recv(header['content-length']))
        
        return header, body

    def _build_response(self, res_body, status):

        json_headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', len(res_body))
        ]

        response = 'HTTP/1.1 {status}\n'.format(status=status)

        for h in json_headers:
            response += '{0}: {1}\n'.format(h[0], h[1])

        response += '\n'
        response += res_body

        return response

    def _init_worker(self, w):

        quit = False

        print('Worker: {} init'.format(w))

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()
                print('Received connection: {}, in worker: {}'.format(client_address, w))

                req_header, req_body = self._parse_request(client_connection)

                # Send request to 'app' to handle it
                res_body, status = self.app(req_header, req_body)
                res = self._build_response(res_body, status)
                
                print(res)
                client_connection.sendall(res.encode())
                client_connection.close()
            except KeyboardInterrupt:
                quit = True

        self.server_socket.close()

    def run(self):
        
        w = 0
        workers = []
       
        # Create pool of workers
        for i in range(self.num_workers):
            p = Process(target=self._init_worker, args=(i,))
            workers.append(p)
            p.start()

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.server_socket.close()

        # Wait to workers to finish
        for j in range(self.num_workers):
            workers[i].join()

        print('Server finished')

def main(ip, port, workers, app_path):
    
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)

    server = Server(ip, port, workers, application)
    print('Server at IP:{ip}, PORT:{port}'.format(ip=ip, port=port))
    server.run()



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
                description='HTTP server',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '--ip',
            default='localhost',
            help='HTTP server IP'
    )
    parser.add_argument(
            '--port',
            type=int,
            default=8888,
            help='HTTP server PORT'
    )
    parser.add_argument(
            '--workers',
            type=int,
            default=1,
            help='Number of workers running the App'
    )
    parser.add_argument(
            '--app',
            help='The app that is going to be run in each worker (module:function)'
    )
    args = parser.parse_args()
    
    main(args.ip, args.port, args.workers, args.app)

