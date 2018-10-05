import json
import logging
import logging.config
import logging.handlers

levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "error": logging.ERROR
}

def init(log_file_name):
    
    config = {}

    with open("log-config.json", "r") as f:
        config = json.load(f)

    config['handlers']['file']['filename'] = log_file_name + '.log'
    config['handlers']['errors']['filename'] = log_file_name + '-errors.log'
    logging.config.dictConfig(config)

def set_queue(q):
    
    qh = logging.handlers.QueueHandler(q)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(qh)

def log(message, level, logger_name):
    
    logger = logging.getLogger(logger_name)
    logger.log(levels[level], message)

def log_worker(q):
    quit = False

    while not quit:
        
        record = q.get()

        if record == None:
            quit = True
            continue
        
        logger = logging.getLogger(record.name)
        logger.handle(record)

