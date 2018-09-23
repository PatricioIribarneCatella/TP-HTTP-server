import socket
import signal
import logger
import parser
from threading import Thread
from multiprocessing import Process, Queue

class Server(object):

    def __init__(self, ip, port, workers, app, fs_scale):
       
        # Create the socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Allow to reuse the same address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Bind
        self.server_socket.bind((ip, port))
        
        # Listen
        self.server_socket.listen(100)

        # Make server's socket inheritable
        self.server_socket.set_inheritable(True)
  
        self.ip = ip
        self.port = port
        self.app = app
        self.num_workers = workers
        self.num_fs = fs_scale
        print("FSs: {}".format(self.num_fs))

    def _init_worker(self, w, log_queue):

        quit = False

        logger.set_queue(log_queue)

        logger.log('Worker: {} init'.format(w),
                    logger.levels["debug"],
                    'http-server')

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, w),
                            logger.levels["debug"],
                            'http-server')

                req_header, req_body = parser.parse_request(client_connection)

                # Send request to 'app' to handle it
                res_body, status = self.app(req_header, req_body, self.num_fs)

                # Log request and response status
                logger.log('(method: {}, path: {}, res_status: {})'.format(
                                req_header["method"],
                                req_header["path"],
                                status), logger.levels["info"], 
                                'http-server')
                
                res = parser.build_response(res_body, status)
                
                print(res)
                client_connection.sendall(res.encode())
                client_connection.close()

            except KeyboardInterrupt:
                quit = True

        self.server_socket.close()

    def run(self):
        
        w = 0
        workers = []
        log_queue = Queue()
       
        # Create pool of workers
        for i in range(self.num_workers):
            p = Process(target=self._init_worker, args=(i, log_queue))
            workers.append(p)
            p.start()
       
        # Set the ignore flag in main process
        # for SIGINT signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Close server connection
        self.server_socket.close()

        logger.init('http-server')
        
        lt = Thread(target=logger.log_worker, args=(log_queue,))
        lt.start()

        # Wait to workers to finish
        for j in range(self.num_workers):
            workers[i].join()

        # Tell the logger to finish
        log_queue.put(None)
        lt.join()

        print('Server finished')

