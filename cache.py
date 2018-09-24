import json

# LRU Cache
#
# Items:
#   uid -> (body, count_old)
#
class Cache(object):

    def __init__(self, size, store_dir):
        self.store_dir = store_dir
        self.data = {}
        self.size = size
        self.count = 0

    def _persist_data(self):

       it = self.data.items()

       s = sorted(it, key=lambda pair: pair[1][1])

       lru = s[0]

       data_lru = self.data[lru[0]]

       with open(self.store_dir + lru[0], "w") as f:
           json.dump(data_lru, f)

       del self.data[lru[0]]

       self.count = self.count - 1

    def _get_max_entry(self):

       if (self.count == 0):
           return 0

       it = self.data.items()

       s = sorted(it, key=lambda pair: pair[1][1])

       new = s.pop()

       return self.data[new[0]][1]

    def empty(self):

        return (self.count == 0)

    def get(self, uid):
        
        if uid not in self.data:
            return None

        item = self.data[uid]

        self.data[uid] = (item[0], item[1] + 1)
        
        return self.data[uid][0]

    def put(self, uid, data):
        
        if (self.count == self.size):
            self._persist_data()

        n = self._get_max_entry()

        self.data[uid] = (data, n + 1)

        self.count = self.count + 1

    def update(self, uid, data):

        if uid not in self.data:
            return False

        self.data[uid][0] = data
        
        return True

    def delete(self, uid):

        if uid in self.data:
            del self.data[uid]
        if (self.count > 0):
            self.count = self.count - 1

