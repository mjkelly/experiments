import socket
import sys
import os
from json import dumps

from httplib2 import Http

CONFIG_PREFIX = "GCHAT_"
CONFIG_REQUIRED_KEYS = ["webhook_url", "bot_name"]

def load_config():
    """Load webhook configuration from the config file."""
    config: dict[str, str] = {}
    for key in CONFIG_REQUIRED_KEYS:
        config[key] = os.getenv(CONFIG_PREFIX + key.upper())
        if not config[key]:
            raise KeyError(f"Missing environment variable: {CONFIG_PREFIX +
                           key.upper()}")
    return config


def send_message(message: str, config: dict[str, str]):
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
