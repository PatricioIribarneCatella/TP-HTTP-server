import json

# Receives header and body
# form request
#   req_header: dictionary
#   req_body: JSON string
#
# Returns: tupple
#   (res_body, status)

def app(req_header, req_body):
    status = '200 OK'
    body = {
            'msg': 'Hello world',
            'count': 11
    }
    if (req_header['method'] == 'GET'):
        res_body = json.dumps(body,
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': '))
    else:
        res_body = req_body

    return res_body, status

