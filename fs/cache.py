#
# LRU Cache (Write-Back)
#
# Items:
#   uid -> (body, count_old, is_in_disc)
#
# Algorithm:
#   
#   - Items are stored in the cache.
#
#   - If the size is reached when an item
#     it's going to be put into it, the LRU
#     algorithm is performed. The LRU item is
#     returned so the File Manager can back up it.
#
#   - If size equals to zero an error code is returned and
#     no element is stored.
#
#   - The 'count_old' field of the items that are stored
#     into the cache is updated (incremented) in every hit.
#     When a new item is stored, the greatest number of the
#     elements that are present in that moment is chosen.
#     The new item is going to have its 'count_old' field 
#     equals to it and incremented in one, to represent that
#     it's new.
#
#   - The 'is_in_disc' field represents an element that has
#     a copy in disc. If the item has to be deleted from the
#     cache it also has to be erased from disc.
#

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.responses as response

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

       self.count -= 1

       r = response.build_cache_full_error({
                        "uid": lru[0],
                        "data": data_lru[0]
       })

       return r

    def _get_max_entry(self):

       if (self.count == 0):
           return 0

       it = self.data.items()

       s = sorted(it, key=lambda pair: pair[1][1])

       new = s.pop()

       return self.data[new[0]][1]

    def get(self, uid):
        
        if uid not in self.data:
            return response.build_not_found_error()

        item = self.data[uid]

        self.data[uid] = (item[0], item[1] + 1, item[2])
        
        return response.build_successful(self.data[uid][0])

    def put(self, uid, data, is_in_disc):
       
        if (self.size == 0):
            r = response.build_cache_zero_error({
                            "uid": uid,
                            "data": data
            })
            return r

        res = uid
        status = response.OK_STATUS

        if (self.count == self.size):
            res, status = self._remove_data()

        n = self._get_max_entry()

        self.data[uid] = (data, n + 1, is_in_disc)

        self.count += 1

        return res, status

    def update(self, uid, data):

        if (self.size == 0):
            return response.build_cache_zero_error("")

        if uid not in self.data:
            return response.build_not_found_error()

        item = self.data[uid]
        self.data[uid] = (data, item[1] + 1, item[2])
        
        return response.build_successful("")

    def delete(self, uid):

        if uid not in self.data:
            return response.build_not_found_error()

        is_in_disc = self.data[uid][2]
        del self.data[uid]
        
        if (self.count > 0):
            self.count -= 1
        
        if (is_in_disc):
            return response.build_in_disc_error("")
        
        return response.build_successful("")

