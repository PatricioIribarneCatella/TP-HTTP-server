import json

class FileManager(object):

    def __init__(self, cache_size):
        
        self.cache_size = cache_size
        
        self.method_handler = {
            'get': self._get_handler,
            'post': self._post_handler,
            'put': self._put_handler,
            'delete': self._del_handler
        }

        self.data = {}

    def _get_handler(self, header, body):
        if header['path'] not in self.data:
            return {'msg': 'not found'}, '404 ERROR'
        return self.data.get(header['path']), '200 OK'

    def _post_handler(self, header, body):
        if header['path'] not in self.data:
            self.data[header['path']] = body
            return {}, '200 OK'
        return {'msg': 'data already exists'}, '405 ERROR'

    def _put_handler(self, header, body):
        if header['path'] not in self.data:
            return {'msg': 'not found'}, '404 ERROR'
        self.data[header['path']] = body
        return {}, '200 OK'

    def _del_handler(self, header, body):
        if header['path'] not in self.data:
            return {'msg': 'not found'}, '404 ERROR'
        del self.data[header['path']]
        return {}, '200 OK'

    def handle_request(self, header, body):

        h = self.method_handler.get(header['method'].lower())
        
        return h(header, body)

