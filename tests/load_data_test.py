import argparse
import requests

URL = "http://localhost:8888/owner/entity"

def main(n):

    print("url: {}\n".format(URL))

    for i in range(n):
        
        print("Request n: {}\n".format(i))
        
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
    args = parser.parse_args()

    main(args.requests)

