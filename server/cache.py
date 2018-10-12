#
# LRU Cache (Write-Back)
#
# Items:
#   uid -> (body, count_old, is_in_disc)
#
# ConcurrentCache extending from 'Cache'
#

import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from utils.cache import Cache
import utils.responses as response

class ConcurrentCache(Cache):

    def __init__(self, size, manager):
        self.data = manager.dict()
        super(ConcurrentCache, self).__init__(size)

