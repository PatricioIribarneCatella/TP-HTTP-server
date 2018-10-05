import ..libs.logger as logger
import ..libs.parser as parser

from threading import Thread

class Replier(Thread):

    def __init__(self, res_queue, conn_queue, log_queue):

        self.res_queue = res_queue
        self.conn_queue = conn_queue
        self.log_queue = log_queue

        super(Replier, self).__init__()

    def run(self):
      
        quit = False
        
        logger.set_queue(self.log_queue)

        while not quit:

            # Get connection from worker process
            c = self.conn_queue.get()

            if (c == None):
                quit = True
                continue

            # Get response from FileManager
            header, res_body, status, address = self.res_queue.get()

            # Log request and response status
            logger.log('(method: {}, path: {}, res_status: {})'.format(
                            header["method"],
                            header["path"],
                            status), "info", 'fs-server')
            
            res = parser.build_response(res_body, status)
            
            c.sendall(res.encode())
            c.close()

