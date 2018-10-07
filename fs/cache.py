import json

# LRU Cache
#
# Items:
#   uid -> (body, count_old, is_in_disc)
#
class Cache(object):

    def __init__(self, size):
        self.data = {}
        self.size = size
        self.count = 0

    def _remove_data(self):

       it = self.data.items()

       s = sorted(it, key=lambda pair: pair[1][1])

       lru = s[0]

       data_lru = self.data[lru[0]]

       del self.data[lru[0]]

       self.count = self.count - 1

       return {"uid": lru[0], "data": data_lru[0]}, "601 OK"

    def _get_max_entry(self):

       if (self.count == 0):
           return 0

       it = self.data.items()

       s = sorted(it, key=lambda pair: pair[1][1])

       new = s.pop()

       return self.data[new[0]][1]

    def get(self, uid):
        
        if uid not in self.data:
            return "", "404 ERROR"

        item = self.data[uid]

        self.data[uid] = (item[0], item[1] + 1, item[2])
        
        return self.data[uid][0], '200 OK'

    def put(self, uid, data, is_in_disc):
       
        if (self.size == 0):
            return {"uid": uid, "data": data}, "602 OK"

        response = uid
        status = '200 OK'

        if (self.count == self.size):
            response, status = self._remove_data()

        n = self._get_max_entry()

        self.data[uid] = (data, n + 1, is_in_disc)

        self.count = self.count + 1

        return response, status

    def update(self, uid, data):

        if (self.size == 0):
            return "", "602 OK"

        if uid not in self.data:
            return "", "404 ERROR"

        item = self.data[uid]
        self.data[uid] = (data, item[1] + 1, item[2])
        
        return "", "200 OK"

    def delete(self, uid):

        if uid not in self.data:
            return response, "404 ERROR"

        is_in_disc = self.data[uid][2]
        del self.data[uid]
        
        if (self.count > 0):
            self.count = self.count - 1
        
        if (is_in_disc):
            return "", "603 OK"
        else:
            return "", "200 OK"

