import time
import requests
import json
import argparse
import eventlet
from datetime import datetime

eventlet.monkey_patch()
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

class RunAction:
    def __init__(self, args):
        self.token = self.get_tokens(args)
        
    def get_tokens(self, args):
        st2_auth_url = args.auth_url + "/tokens"
        header = {
            "Content-Type": "application/json"
        }
        auth = (args.st2user, args.st2passwd)
        res = requests.post(st2_auth_url, headers=header,
                            auth=auth, verify=False).text
        return json.loads(res)["token"]

    def get_req(self, url, token):
        header = {
            "Content-Type": "application/json",
            "X-Auth-Token": "{}".format(token)
        }
        return requests.get(url, headers=header, verify=False)

    def post_req(self, url, token, data):
        header = {
            "Content-Type": "application/json",
            "X-Auth-Token": "{}".format(token)
        }
        return requests.post(url, headers=header, data=data, verify=False)

    def run_action(self, args):
        st2_action_url = args.api_url + "/executions"
        data = '''{
            "action": "%s",
            "parameters": {
                "message": "This is test from benchmark"
            }
        }''' % (args.action_ref)
        return json.loads(self.post_req(url=st2_action_url, token=self.token, data=data).text)

    def get_execution_info(self, args, action_id):
        st2_execion_info_url = args.api_url + \
            "/executions/{}".format(action_id)
        return json.loads(self.get_req(url=st2_execion_info_url, token=self.token).text)


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        Run st2 actions.
        """
    )
    parser.add_argument(
        "--st2user",
        required=True,
        help=(
            "st2 user"
        ),
    )
    parser.add_argument(
        "--st2passwd",
        required=True,
        help=(
            "st2 password "
        ),
    )
    parser.add_argument(
        "--action-ref",
        required=True,
        help=(
            "Action to be executed "
        ),
    )
    parser.add_argument(
        "--auth-url",
        default="https://127.0.0.1:9101",
        help=(
            "st2 auth url "
        ),
    )
    parser.add_argument(
        "--api-url",
        default="https://127.0.0.1:9100",
        help=(
            "st2 api url "
        ),
    )
    args = parser.parse_args()
    return args


def get_elapsed_time(log_dict):
    elapsed_time = {}
    start_time = None
    for process in log_dict:
        if start_time is None:
            start_time = datetime.strptime(process["timestamp"], DATE_FORMAT)
            continue
        complete_time = datetime.strptime(process["timestamp"], DATE_FORMAT)
        elapsed_time[process["status"]] = (
            complete_time - start_time).total_seconds()
        start_time = complete_time
    return elapsed_time

def run(args):
    runner = RunAction(args)
    action_id = runner.run_action(args)["id"]
    time.sleep(3)
    return runner.get_execution_info(args, action_id)["log"]

def main():
    pool = eventlet.GreenPool()
    result = []
    args = parse_args()
    for i in range(5):
        result.append(pool.spawn(run, args))
    pool.waitall()
    print(result)

if __name__ == "__main__":
    main()
