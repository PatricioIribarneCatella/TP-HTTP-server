#
# LRU Cache (Write-Back)
#
# Items:
#   uid -> (body, count_old, is_in_disc)
#
# FileCache extending from 'Cache'
#

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import utils.cache as Cache
import utils.responses as response

class FileCache(Cache):

    def __init__(self, size):
        self.data = {}
        super(FileCache, self).__init__(size)

