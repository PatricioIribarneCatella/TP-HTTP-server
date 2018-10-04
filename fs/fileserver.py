import signal
import ../libs/logger

from threading import Thread
from filemanager import FileManager
from ../libs/socket import Socket

from multiprocessing import Process, Queue

class FileServer(object):

    def __init__(self, ip, port, workers, cache_size):
       
        # Create the socket
        self.server_socket = Socket(ip, port, max_conn)
  
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
                            status), "info", 'fs-server')
            
            res = parser.build_response(res_body, status)
            
            c.sendall(res.encode())
            c.close()

 
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
            workers[j].join()

        # Tell the Cache and Fs controller to finish
        req_queue.put(None)
        c.join()

        # Tell the logger to finish
        log_queue.put(None)
        lt.join()

        print('File System server finished')

