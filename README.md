# TP-HTTP-server

HTTP server concurrente (Sistemas Distribuidos I)

### Ejecutar

```bash
$ python3 main.py --app=[module:function] [--workers=NUM(1) | --ip=IP(localhost) | --port=PORT(8888) ]
```
En otra terminal ejecutar:

```bash
$ python3 fs.py [--fsworkers=NUM(1) | --ip=IP(localhost) | --port=PORT(8888) | --cache=SIZE(100 entries)]
```

#### Docker

- Dependencias: _Docker_ y _Docker Compose_

```bash
$ ./run.sh FSs --workers=NUM --fsworkers=NUM --cache=SIZE --urlfs=URL

	FSs: Cantidad de containers para el File System
	URL: El nombre o url donde se encuentra el FS
```

#### Tests

- Dependencias: _requests_

```bash
$ python3 load_data_test.py [--requests=NUM | --testers=NUM]
```

