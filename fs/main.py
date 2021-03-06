import argparse
from fileserver import FileServer

def main(ip, port, workers, cache_size, max_conn):

    print('FS Server at IP:{ip}, PORT:{port}'.format(ip=ip, port=port))
    
    server = FileServer(ip, port, workers, cache_size, max_conn)
    server.run()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
                description='FS server',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '--ip',
            default='0.0.0.0',
            help='FS server IP'
    )
    parser.add_argument(
            '--port',
            type=int,
            default=9999,
            help='FS server PORT'
    )
    parser.add_argument(
            '--fsworkers',
            type=int,
            default=1,
            help='Number of workers running the FS App'
    )
    parser.add_argument(
            '--fscache',
            type=int,
            default=100,
            help='Number of entries in the cache'
    )
    parser.add_argument(
            '--connections',
            type=int,
            default=100,
            help='The max number of waiting connections per worker'
    )
    args = parser.parse_args()
    
    main(args.ip, args.port, args.fsworkers,
            args.fscache, args.connections)

