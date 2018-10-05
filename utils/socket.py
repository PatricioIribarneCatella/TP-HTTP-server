import socket

class Socket(object):

    def __init__(self, ip, port, max_conn):

        # Create the socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Allow to reuse the same address (time-out after closing socket)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Allow to reuse the same bind port in multiple process and
        # perform an 'accept()' round-robin of them
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Bind
        self.socket.bind((ip, port))
        
        # Listen
        self.socket.listen(max_conn)

        # Make server's socket inheritable
        self.socket.set_inheritable(True)

    def accept(self):
        return self.socket.accept()

    def close(self):
        self.socket.close()

