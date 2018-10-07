import sys
import signal
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.logger as logger
from utils.socket import Socket

from worker import Worker
from processor import HttpProcessor

from multiprocessing import Process, Queue

class Server(object):

    def __init__(self, ip, port, workers, num_fs, url_fs, max_conn):
       
        # Create the socket
        self.server_socket = Socket(ip, port, max_conn)

        self.ip = ip
        self.port = port
        self.num_workers = workers
        self.processor = HttpProcessor(num_fs, url_fs)

    def run(self):
        
        workers = []
        log_queue = Queue()
       
        # Create pool of workers
        for i in range(self.num_workers):
            w = Worker(i, self.processor, self.server_socket, log_queue)
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
        # Wait for logger
        logging.join()

        print('Server finished')

