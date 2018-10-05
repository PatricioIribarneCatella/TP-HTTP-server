import signal
import ../libs/logger

from dispatcher import Dispatcher
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

    def run(self):
        
        w = 0
        dispatchers = []
        
        log_queue = Queue()
        req_queue = Queue()
        res_queues = [Queue() for i in range(self.num_workers)]
       
        # Create pool of dispatchers
        for i in range(self.num_workers):
            d = Dispatcher(i, self.server_socket, req_queue, res_queues[i], log_queue)
            dispatchers.append(d)
            d.start()
       
        # Set the ignore flag in main process
        # for SIGINT signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Close server connection
        self.server_socket.close()
        
        # Create Cache and FS controller
        c = Process(target=self._init_file_manager, args=(req_queue, res_queues))
        c.start()

        logger.init('fs-server')
        
        lp = Process(target=logger.log_worker, args=(log_queue,))
        lp.start()

        # Wait to workers to finish
        for j in range(self.num_workers):
            dispatchers[j].join()

        # Tell the Cache and Fs controller to finish
        req_queue.put(None)
        c.join()

        # Tell the logger to finish
        log_queue.put(None)
        lp.join()

        print('File System server finished')

