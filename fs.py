import argparse
from fs-server import FSServer

def main(ip, port, workers, app_path):
    
    module, app = app_path.split(':')
    module = __import__(module)
    app = getattr(module, app)

    print('Server at IP:{ip}, PORT:{port}'.format(ip=ip, port=port))
    
    server = FSServer(ip, port, workers, app)
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
            default=8888,
            help='FS server PORT'
    )
    parser.add_argument(
            '--workers',
            type=int,
            default=1,
            help='Number of workers running the FS App'
    )
    parser.add_argument(
            '--cache-size',
            type=int,
            default=10,
            help='Number of entries in the cache'
    )
    args = parser.parse_args()
    
    main(args.ip, args.port, args.workers, args.cache-size)

