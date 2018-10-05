from multiprocessing import Process

class RequestExec(Process):

    def __init__(self, req_queue, res_queues, cache_size):

        self.req_queue = req_queue
        self.res_queues = res_queues
        self.cache_size = cache_size

        super(RequestExec, self).__init__()

    def run(self):

        quit = False

        while not quit:
            
            # (req_header, req_body, pid, address)
            req = self.req_queue.get()

            if (req == None):
                quit = True
                continue

            header = req[0]
            body = req[1]
            pid = req[2]
            address = req[3]

            handler = self.method_handler.get(header['method'].lower())

            res_body, status = handler(header, body)

            self.res_queues[pid].put((header, res_body, status, address))

