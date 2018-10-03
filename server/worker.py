import ../libs/logger
from multiprocessing import Process

class Worker(Process):

    def __init__(self, wid, log_queue, server_socket):

        self.server_socket = server_socket
        self.log_queue = log_queue
        self.wid = wid

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

                req_header, req_body = parser.parse_request(client_connection)

                # Send request to 'app' to handle it
                res_body, status = self.app(req_header,
                                            req_body,
                                            self.num_fs,
                                            self.url_fs)

                # Log request and response status
                logger.log('(method: {}, path: {}, res_status: {})'.format(
                                req_header["method"],
                                req_header["path"],
                                status), "info", 'http-server')
                
                res = parser.build_response(res_body, status)
                
                client_connection.sendall(res.encode())
                client_connection.close()

            except KeyboardInterrupt:
                quit = True

        self.server_socket.close()

