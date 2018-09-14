import sys
import socket
import argparse
from multiprocessing import Process, Queue

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
        
        self.ip = ip
        self.port = port
        self.app = app
        self.num_workers = workers

    def _parse_request(client_connection):

        req = client_connection.recv(1024)

        ### Parse the data

    def run():
        
        w = 0

        queues = [Queue()
                    for i in xrange(self.num_workers)]
        workers = [Process(target=self.app, args=(queues[i],).start())
                    for i in xrange(self.num_workers)]

        while (True):

            # Accept client connection
            client_connection, client_address = self.server_socket.accept()
            
            # Dispatch the connection to a worker
            queues[w++ % self.num_workers].put(self._parse_request(client_connection))

            # Close the connection from the master
            client_connection.close()


def main(ip, port, workers, app_path):
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)

    server = Server(ip, port, workers, application)
    server.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='HTTP server',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '--ip',
            type=string,
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
            type=string
            default=None
            help='The app that is going to be run in each worker'
    )
    args = parser.parse_args()
    main(args.ip, args.port, args.workers, args.app)

