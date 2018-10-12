import os
import argparse
from server import Server

def main(ip, port, workers, url_fs, cache_size, max_conn):
    
    print('Server at IP:{ip}, PORT:{port}'.format(ip=ip, port=port))

    num_fs = int(os.getenv('FS_SCALE', 1))

    server = Server(ip, port, workers, cache_size,
                    num_fs, url_fs, max_conn)
    server.run()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
                description='HTTP server',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '--ip',
            default='0.0.0.0',
            help='HTTP server IP'
    )
    parser.add_argument(
            '--port',
            type=int,
            default=8888,
            help='HTTP server PORT'
    )
    parser.add_argument(
            '--workers',
            type=int,
            default=1,
            help='Number of workers running the App'
    )
    parser.add_argument(
            '--urlfs',
            default='localhost',
            help='File System network name'
    )
    parser.add_argument(
            '--cache',
            type=int,
            default=100,
            help='The cache size'
    )
    parser.add_argument(
            '--connections',
            type=int,
            default=100,
            help='The max number of waiting connections per worker'
    )
    args = parser.parse_args()
    
    main(args.ip, args.port, args.workers,
            args.urlfs, args.cache, args.connections)

