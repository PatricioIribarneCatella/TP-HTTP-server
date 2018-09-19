import socket
import signal
from utils import RequestParser
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

        # Make server's socket inheritable
        self.server_socket.set_inheritable(True)
        
        self.ip = ip
        self.port = port
        self.app = app
        self.num_workers = workers
        self.parser = RequestParser()

    def _init_worker(self, w):

        quit = False

        print('Worker: {} init'.format(w))

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()
                print('Received connection: {}, in worker: {}'.format(client_address, w))

                req_header, req_body = self.parser.parse_request(client_connection)

                # Send request to 'app' to handle it
                res_body, status = self.app(req_header, req_body)
                
                res = self.parser.build_response(res_body, status)
                
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
        
        # Set the ignore flag in main process
        # for SIGINT signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Close server connection
        self.server_socket.close()

        # Wait to workers to finish
        for j in range(self.num_workers):
            workers[i].join()

        print('Server finished')


