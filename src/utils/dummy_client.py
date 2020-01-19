import requests
import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='server address')
    parser.add_argument('--host', type=str, default='127.0.0.1:5000')
    parser.add_argument('--interval', type=int, default=1)
    args = parser.parse_args()
    host = args.host
    interval = args.interval
    url = 'http://' + host + '/report'
    while True:
        try:
            content = {"device_id":"dummy_sensor", "name":"dummy", "status": "on"}
            r = requests.post(url, json=content)
            if r.ok:
                print(r.text)
            time.sleep(interval*60)
        except Exception as e:
            print("Error occurs!")
            print(repr(e))

