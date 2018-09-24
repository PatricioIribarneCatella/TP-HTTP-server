import argparse
import requests
from multiprocessing import Process

URL = "http://localhost:8888/owner/entity"

def _work(n, p):
    
    for i in range(n):
        
        print("Request n: {}, tester: {}\n".format(i, p))
        
        # POST request
        print("POST request")
        print("curl --header {header} --data {data} {url}".format(
                    data={"username": "user_" + str(i), "password": "pass_" + str(i)},
                    header='Content-Type: application/json',
                    url=URL))

        payload = {"username": "user_" + str(i), "password": "pass_" + str(i)}
        pr = requests.post(URL, json=payload)

        print("Status code: {}".format(pr.status_code))
        
        res = pr.json()
        print("Body: {}\n".format(res))

        uid = res['id']

        # GET request
        print("GET request")
        print("curl {}".format(URL + "/" +  uid))

        gr = requests.get(URL + "/" +  uid)

        print("Status code: {}".format(gr.status_code))
        print("Body: {}\n\n".format(gr.json()))

def main(n, ps):

    print("url: {}\n".format(URL))

    testers = [Process(target=_work, args=(n, i)) for i in range(ps)]

    for i in range(ps):
        testers[i].start()

    for j in range(ps):
        testers[j].join()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description="HTTP Tests",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
            '--requests',
            type=int,
            default=1,
            help="Number of requests to do"
    )
    parser.add_argument(
            '--testers',
            type=int,
            default=1,
            help="Numbre of workers sending requests"
    )
    args = parser.parse_args()

    main(args.requests, args.testers)

