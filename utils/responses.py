#
# Response builder with data and status codes
#

OK_STATUS = '200 OK'
NOT_FOUND_STATUS = '404 ERROR'
BAD_ID_STATUS = '405 ERROR'
INTERNAL_ERROR_STATUS = '500 ERROR'
CACHE_FULL_STATUS = '601 OK'
CACHE_ZERO_SIZE_STATUS = '602 OK'
IN_DISC_STATUS = '603 OK'

def build_id_error(error):
    return {'msg': error}, BAD_ID_STATUS

def build_internal_error():
    return {'msg': 'internal error'}, INTERNAL_ERROR_STATUS

def build_cache_full_error(data):
    return data, CACHE_FULL_STATUS

def build_cache_zero_error(data):
    return data, CACHE_ZERO_SIZE_STATUS

def build_not_found_error():
    return {'msg': 'not found'}, NOT_FOUND_STATUS

def build_successful(data):
    return data, OK_STATUS

def build_in_disc_error(data):
    return data, IN_DISC_STATUS

