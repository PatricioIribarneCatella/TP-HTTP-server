import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.logger as logger
import utils.parser as parser

from threading import Thread
from multiprocessing import Process, Queue

class Worker(Process):

    def __init__(self, wid, app, server_socket, log_queue):

        self.server_socket = server_socket
        self.log_queue = log_queue
        self.wid = wid
        self.app = app

        super(Worker, self).__init__()

    def _request_processing(self, conn_queue):

        quit = False

        while not quit:

            client_connection = conn_queue.get()

            if (client_connection == None):
                quit = True
                continue

            # Parse request
            req_header, req_body = parser.parse_request(client_connection)

            # Send request to 'APP' to handle it
            res_body, res_status = self.app.exec_request(req_header, req_body)

            # Log request and response status
            logger.log('(method: {}, path: {}, res_status: {})'.format(
                            req_header["method"],
                            req_header["path"],
                            res_status), "info", 'http-server', self.log_queue)
            
            res = parser.build_response(res_body, res_status)
            
            # Send response to client
            client_connection.sendall(res.encode())
            client_connection.close()


    def run(self):
        
        quit = False

        conn_queue = Queue()

        sub_worker = Thread(target=self._request_processing, args=(conn_queue,))
        sub_worker.start()

        logger.log('Worker: {} init'.format(self.wid),
                    "debug", 'http-server', self.log_queue)

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, self.wid),
                            "debug", 'http-server', self.log_queue)

                conn_queue.put(client_connection)

            except KeyboardInterrupt:
                quit = True

        # Tell the sub worker to finish
        conn_queue.put(None)
        sub_worker.join()

        self.server_socket.close()

