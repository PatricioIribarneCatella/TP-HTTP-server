import os
import argparse
from server import Server

def main(ip, port, workers, app_path, url_fs):
    
    module, app = app_path.split(':')
    module = __import__(module)
    app = getattr(module, app)

    print('Server at IP:{ip}, PORT:{port}'.format(ip=ip, port=port))
    
    server = Server(ip, port,
                workers, app,
                int(os.getenv('FS_SCALE', 1)),
                url_fs)
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
            '--app',
            help='The app that is going to be run in each worker (module:function)'
    )
    args = parser.parse_args()
    
    main(args.ip, args.port, args.workers, args.app, args.urlfs)

