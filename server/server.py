import signal
import ../libs/logger
import ../libs/parser
from ../libs/socket import Socket
from multiprocessing import Process, Queue

class Server(object):

    def __init__(self, ip, port, workers, num_fs, url_fs):
       
        # Create the socket
        self.server_socket = Socket(ip, port, max_conn=100)

        self.ip = ip
        self.port = port
        self.num_workers = workers
        self.app = App(num_fs, url_fs)


    def _init_worker(self, w, log_queue):

        quit = False

        logger.set_queue(log_queue)

        logger.log('Worker: {} init'.format(w),
                    "debug", 'http-server')

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, w),
                            "debug", 'http-server')

                req_header, req_body = parser.parse_request(client_connection)

                # Send request to 'app' to handle it
                res_body, status = self.app(req_header,
                                            req_body,
                                            self.num_fs,
                                            self.url_fs)

                # Log request and response status
                logger.log('(method: {}, path: {}, res_status: {})'.format(
                                req_header["method"],
                                req_header["path"],
                                status), "info", 'http-server')
                
                res = parser.build_response(res_body, status)
                
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

