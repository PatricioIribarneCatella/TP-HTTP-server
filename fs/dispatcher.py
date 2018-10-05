import ..libs.logger as logger

from replier import Replier
from dispatcher import Dispatcher

from multiprocessing import Process, Queue

class Dispatcher(Process):

    def __init__(self, pid, server_socket, req_queue, res_queue, log_queue):
        
        self.server_socket = server_socket
        self.req_queue = req_queue
        self.res_queue = res_queue
        self.log_queue = log_queue
        self.pid = pid

        super(Dispatcher, self).__init__()
    
    def run(self):
        
        quit = False
        conn_queue = Queue()
        
        # Create Replier thread to handle connections
        # and responses from the Executor
        rep = Replier(self.res_queue, conn_queue, self.log_queue)
        rep.start()

        logger.set_queue(self.log_queue)
        
        logger.log('Dispatcher: {} init'.format(self.pid),
                    "debug", 'fs-server')

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, self.pid),
                            "debug", 'fs-server')

                # Parse request
                req_header, req_body = parser.parse_request(client_connection)
                
                # Send request to Executor
                req_queue.put((req_header, req_body, w, client_address))

                # Send connection to Replier
                conn_queue.put(client_connection)

            except KeyboardInterrupt:
                quit = True

        # Wait for response thread to finish
        conn_queue.put(None)
        rep.join()

        self.server_socket.close()

