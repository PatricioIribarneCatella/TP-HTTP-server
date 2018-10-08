# TP-HTTP-server

HTTP server concurrente (Sistemas Distribuidos I)

### Ejecutar

```bash
$ python3 server/main.py [--workers=NUM(1) |
			  --ip=IP('localhost') |
			  --port=PORT(8888) |
			  --urlfs=URL('localhost') |
			  --connections=MAX_CONN(100)]
```
En otra terminal ejecutar:

```bash
$ python3 fs/main.py [--fsworkers=NUM(1) |
		      --ip=IP('localhost') |
		      --port=PORT(9999) | 
		      --cache=SIZE(100 entries) |
		      --connections=MAX_CONN(100)]
```

#### Docker

- Dependencias: [_Docker_](https://docs.docker.com/install/) y [_Docker Compose_](https://docs.docker.com/compose/install/)

```bash
$ ./run.sh --fs=FSs --workers=NUM --fsworkers=NUM --cache=SIZE [--urlfs=URL('http_fs_')]

	FSs: Cantidad de containers para el File System
	URL: El nombre o url donde se encuentra el FS
```

#### Tests

- Dependencias: [_requests_](http://www.python-requests.org/en/master/)

```bash
$ python3 load_data_test.py [--requests=NUM | --testers=NUM]
```

