# Protocol Decoder and Encoder for sending 
# and receiving requests to File System Server
#
# Format:
#
# Request:
#   ---------------------------------------------------
#   | OPCODE | '\n' | PATH | '\n' | LEN | '\n' | DATA |
#   ---------------------------------------------------
#
# Response:
#   -------------------------------------
#   | STATUS | '\n' | LEN | '\n' | DATA |
#   -------------------------------------
#

# Mapping of HTTP methods to OPCODES
opcodes = {
    "get": '1',
    "post": '2',
    "put": '3',
    "delete": '4'
}

# Mapping of OPCODES to HTTP methods
methods = {
    "1": "get",
    "2": "post",
    "3": "put",
    "4": "delete"
}

# Obtains a line from the socket
def _get_line(connection, delimeter):

    c = connection.recv(1)
    line = ""

    while (c.decode() != delimeter):
        line = line + c.decode()
        c = connection.recv(1)

    return line.rstrip('\r')

def encode_request(header, body):

    body = json.dumps(body)

    req = opcodes[header["method"]] +
          '\n' +
          header["path"] +
          '\n' +
          str(len(body)) +
          '\n' +
          body

    return req 

def decode_request(connection):

    opcode = _get_line(connection, '\n')

    path = _get_line(connection, '\n')

    length = _get_line(connection, '\n')

    body = connection.recv(int(length) + 1)

    method = methods[opcode]

    return {"method": method, "path": path}, body

def encode_response(body, status):

    body = json.dumps(body)

    res = status +
          '\n' +
          str(len(body)) +
          '\n' +
          body

    return res

def decode_response(connection):

    status = _get_line(connection, '\n')

    length = _get_line(connection, '\n')

    body = connection.recv(int(length) + 1)

    return {
        "status": status,
        "body": body    
    }

