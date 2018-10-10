import sys
import signal
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.logger as logger
from utils.socket import Socket

from cache import Cache
from worker import Worker

from multiprocessing import Process, Queue, Manager

class Server(object):

    def __init__(self, ip, port, workers, cache_size,
                    num_fs, url_fs, max_conn):
       
        # Create the socket
        self.server_socket = Socket(ip, port, max_conn)

        self.ip = ip
        self.port = port
        self.num_workers = workers
        self.cache_size = cache_size
        self.num_fs = num_fs
        self.url_fs = url_fs

    def run(self):
        
        workers = []
        log_queue = Queue()

        cache = Cache(self.cache_size, Manager())

        # Create pool of workers
        for i in range(self.num_workers):
            w = Worker(i, self.server_socket,
                        log_queue, cache,
                        self.url_fs, self.num_fs)
            workers.append(w)
            w.start()
       
        # Set the ignore flag in main process
        # for SIGINT signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        # Close server connection
        self.server_socket.close()

        logger.init('http-server')
        
        logging = Process(target=logger.log_worker, args=(log_queue,))
        logging.start()

        # Wait to workers to finish
        for j in range(self.num_workers):
            workers[j].join()

        # Tell the logger to finish
        log_queue.put(None)
        logging.join()

        print('Server finished')

