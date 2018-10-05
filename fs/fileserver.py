import signal

import ..libs.logger as logger
from ..libs.socket import Socket

from dispatcher import Dispatcher
from executor import RequestExec

from multiprocessing import Process, Queue

class FileServer(object):

    def __init__(self, ip, port, workers, cache_size):
       
        # Create the socket
        self.server_socket = Socket(ip, port, max_conn)
  
        self.ip = ip
        self.port = port
        self.num_workers = workers
        self.cache_size = cache_size

    def run(self):

        dispatchers = []
        
        logger.init('fs-server')
        
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
        r = RequestExec(req_queue, res_queues, self.cache_size)
        r.start()

        # Create 'logger' process
        lp = Process(target=logger.log_worker, args=(log_queue,))
        lp.start()

        # Wait for dispatchers to finish
        for j in range(self.num_workers):
            dispatchers[j].join()

        # Tell the 'RequestExec' to finish
        req_queue.put(None)
        r.join()

        # Tell the 'logger' to finish
        log_queue.put(None)
        lp.join()

        print('File System server finished')

