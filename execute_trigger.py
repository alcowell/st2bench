import requests
import json
import argparse

class ExecuteTrigger:
    def __init__(self, args):
        self.token = self.get_token(args)
        print(self.token)

    def get_token(self, args):
        st2_auth_url = args.auth_url + "/tokens"
        header = {
            "Content-Type": "application/json"
        }
        auth = (args.st2user, args.st2passwd)
        res = requests.post(st2_auth_url, headers=header,
                            auth=auth, verify=False).text
        print(res)
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
            "X-Auth-Token": "{}".format(token),
            "St2-Trace-Tag": "bitch-3"
        }
        return requests.post(url, headers=header, data=data, verify=False)

    def execute_trigger(self, args):
        st2_webhook_url = args.api_url + "/webhooks/st2"
        data = {
            "trigger": "zabbix.event_handler",
            "payload": {
                "alert_sendto": "root@localhost",
                "alert_subject": "yeah",
                "alert_message": "hoge",
                "extra_args": ["hoge"]
            },
            "trace_tag": "bitch"
        }
        data2 = '{"trigger": "zabbix.event_handler", "payload": {"attribute1": "value1"}}'
        return self.post_req(st2_webhook_url, token=self.token, data=json.dumps(data)).text

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

if __name__ == "__main__":
    args = parse_args()
    runner = ExecuteTrigger(args)
    print(runner.execute_trigger(args))
