import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.parser as parser
import utils.logger as logger

from replier import Replier

from multiprocessing import Process, Queue

class Dispatcher(Process):

    def __init__(self, dis_id, server_socket, req_queue, res_queue, log_queue):
        
        self.server_socket = server_socket
        self.req_queue = req_queue
        self.res_queue = res_queue
        self.log_queue = log_queue
        self.dis_id = dis_id

        super(Dispatcher, self).__init__()
    
    def run(self):
        
        quit = False
        conn_queue = Queue()
        
        logger.log('Dispatcher: {} init'.format(self.dis_id),
                    "info", 'fs-server', self.log_queue)

        # Create Replier thread to handle connections
        # and responses from the Executor
        rep = Replier(self.res_queue, conn_queue, self.log_queue)
        rep.start()
        
        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, self.dis_id),
                            "debug", 'fs-server', self.log_queue)

                # Parse request
                req_header, req_body = parser.parse_request(client_connection)
                
                # Send request to Executor
                self.req_queue.put((req_header, req_body, self.dis_id, client_address))

                # Send connection to Replier
                conn_queue.put(client_connection)

            except KeyboardInterrupt:
                quit = True

        # Wait for response thread to finish
        conn_queue.put(None)
        rep.join()

        self.server_socket.close()

