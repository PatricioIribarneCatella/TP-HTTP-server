import socket
import signal
import logger
import parser
import queue
from threading import Thread
from filemanager import FileManager
from multiprocessing import Process, Queue

class FSServer(object):

    def __init__(self, ip, port, workers, cache_size):
       
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
        self.num_workers = workers
        self.cache_size = cache_size

    def _init_file_manager(self, req_queue, res_queues):

        fm = FileManager(self.cache_size)

        fm.handle_request(req_queue, res_queues)

    def _wait_response(self, res_queue, conn_queue):
      
        quit = False

        while not quit:

            # Get connection from worker process
            c = conn_queue.get()

            if (c == None):
                quit = True
                continue

            # Get response from FileManager
            header, res_body, status, address = res_queue.get()

            # Log request and response status
            logger.log('(method: {}, path: {}, res_status: {})'.format(
                            header["method"],
                            header["path"],
                            status), logger.levels["info"],
                            'fs-server')
            
            res = parser.build_response(res_body, status)
            
            c.sendall(res.encode())
            c.close()

    def _init_worker(self, w, log_queue, req_queue, res_queue):

        quit = False
        conn_queue = Queue()
        
        logger.set_queue(log_queue)

        res_t = Thread(target=self._wait_response, args=(res_queue, conn_queue))
        res_t.start()

        logger.log('Worker: {} init'.format(w),
                    logger.levels["debug"],
                    'fs-server')

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, w),
                            logger.levels["debug"],
                            'fs-server')

                # Parse request
                req_header, req_body = parser.parse_request(client_connection)
                
                # Send request to file manager controller
                req_queue.put((req_header, req_body, w, client_address))
                conn_queue.put(client_connection)

            except KeyboardInterrupt:
                quit = True

        # Wait for response thread to finish
        conn_queue.put(None)
        res_t.join()

        self.server_socket.close()

    def run(self):
        
        w = 0
        workers = []
        
        log_queue = Queue()
        req_queue = Queue()
        res_queues = [Queue() for i in range(self.num_workers)]
       
        # Create pool of workers
        for i in range(self.num_workers):
            p = Process(target=self._init_worker,
                    args=(i, log_queue, req_queue, res_queues[i]))
            workers.append(p)
            p.start()
       
        # Set the ignore flag in main process
        # for SIGINT signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Close server connection
        self.server_socket.close()
        
        # Create Cache and FS controller
        c = Process(target=self._init_file_manager, args=(req_queue, res_queues))
        c.start()

        logger.init('fs-server')
        
        lt = Thread(target=logger.log_worker, args=(log_queue,))
        lt.start()

        # Wait to workers to finish
        for j in range(self.num_workers):
            workers[i].join()

        # Tell the Cache and Fs controller to finish
        req_queue.put(None)
        c.join()

        # Tell the logger to finish
        log_queue.put(None)
        lt.join()

        print('File System server finished')

