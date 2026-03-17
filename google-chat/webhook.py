import socket
import sys
from json import dumps

import yaml
from httplib2 import Http

CONFIG_FILE = "config.yaml"
CONFIG_REQUIRED_KEYS = ["webhook_url", "bot_name"]

def load_config():
    """Load webhook configuration from the config file."""
    with open(CONFIG_FILE, "r") as config_file:
        config_data = yaml.safe_load(config_file)
    for key in CONFIG_REQUIRED_KEYS:
        if key not in config_data:
            raise KeyError(f"Missing required config key: {key}")
    return config_data


def send_message(message: str, config):
    host = socket.gethostname()
    app_message = {
        "text": f"{message} [from {config['bot_name']} on {host}]",
    }
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    return http_obj.request(
        uri=config["webhook_url"],
        method="POST",
        headers=message_headers,
        body=dumps(app_message),
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python webhook.py <message>")
        return
    message = sys.argv[1]
    config = load_config()
    print(send_message(message, config))


if __name__ == "__main__":
    main()
