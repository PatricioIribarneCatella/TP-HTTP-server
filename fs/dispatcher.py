from multiprocessing import Process

class Dispatcher(Process):

    def __init__(self):
        # initialize

    def _wait_response(self, res_queue, conn_queue):
      
        quit = False

        while not quit:

            # Get connection from worker process
            c = conn_queue.get()

            if (c == None):
                quit = True
                continue

            # Get response from FileManager
            header, res_body, status, address = res_queue.get()

            # Log request and response status
            logger.log('(method: {}, path: {}, res_status: {})'.format(
                            header["method"],
                            header["path"],
                            status), "info", 'fs-server')
            
            res = parser.build_response(res_body, status)
            
            c.sendall(res.encode())
            c.close()

    def run(self):
        
        quit = False
        conn_queue = Queue()
        
        logger.set_queue(log_queue)

        res_t = Thread(target=self._wait_response, args=(res_queue, conn_queue))
        res_t.start()

        logger.log('Worker: {} init'.format(w),
                    "debug", 'fs-server')

        while not quit:

            try:
                # Accept client connection
                client_connection, client_address = self.server_socket.accept()

                logger.log('Received connection: {}, in worker: {}'.format(client_address, w),
                            "debug", 'fs-server')

                # Parse request
                req_header, req_body = parser.parse_request(client_connection)
                
                # Send request to file manager controller
                req_queue.put((req_header, req_body, w, client_address))
                conn_queue.put(client_connection)

            except KeyboardInterrupt:
                quit = True

        # Wait for response thread to finish
        conn_queue.put(None)
        res_t.join()

        self.server_socket.close()

