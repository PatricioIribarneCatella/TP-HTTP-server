import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.logger as logger
import utils.parser as parser

from multiprocessing import Process

class Worker(Process):

    def __init__(self, wid, app, server_socket, log_queue):

        self.server_socket = server_socket
        self.log_queue = log_queue
        self.wid = wid
        self.app = app

        super(Worker, self).__init__()

    def run(self):
        
        quit = False

        logger.set_queue(self.log_queue)

        logger.log('Worker: {} init'.format(self.wid),
                    "debug", 'http-server')

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, self.wid),
                            "debug", 'http-server')

                # Parse request
                req_header, req_body = parser.parse_request(client_connection)

                # Send request to 'APP' to handle it
                res_body, res_status = self.app.exec_request(req_header, req_body)

                # Log request and response status
                logger.log('(method: {}, path: {}, res_status: {})'.format(
                                req_header["method"],
                                req_header["path"],
                                res_status), "info", 'http-server')
                
                res = parser.build_response(res_body, res_status)
                
                # Send response to client
                client_connection.sendall(res.encode())
                client_connection.close()

            except KeyboardInterrupt:
                quit = True

        self.server_socket.close()

