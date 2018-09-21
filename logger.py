import logging
import logging.config
import logging.handlers

config = {
    'version': 1,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'http-server.log',
            'mode': 'w',
            'level': 'INFO',
            'formatter': 'detailed',
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': 'http-server-errors.log',
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'detailed',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file', 'errors']
    },
}

levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "error": logging.ERROR
}

def init():
    logging.config.dictConfig(config)

def set_queue(q):
    
    qh = logging.handlers.QueueHandler(q)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(qh)

def log(message, level, logger_name):
    
    logger = logging.getLogger(logger_name)
    logger.log(level, message)

def log_worker(q):
    quit = False

    while not quit:
        
        record = q.get()

        if record == None:
            quit = True
            continue
        
        logger = logging.getLogger(record.name)
        logger.handle(record)

