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

    with open("./utils/log-config.json", "r") as f:
        config = json.load(f)

    config['handlers']['file']['filename'] = log_file_name + '.log'
    config['handlers']['errors']['filename'] = log_file_name + '-errors.log'
    logging.config.dictConfig(config)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

def log(message, level, logger_name, log_queue):
    
    log_queue.put({
        "message": message,
        "level": levels[level],
        "name": logger_name
    })

def log_worker(q):

    quit = False

    while not quit:
        
        record = q.get()

        if record == None:
            quit = True
            continue
        
        name = record["name"]
        level = record["level"]
        msg = record["message"]

        logger = logging.getLogger(name)
        logger.log(level, msg)

