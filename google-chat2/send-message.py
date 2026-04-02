from json import dumps, load
from httplib2 import Http
from sys import argv
from os import getenv
import os.path

CONFIG_FILE = os.path.join(getenv('HOME'), '.google-webhook-message.json')

def main():
    '''Send a message to Google Chat.'''
    with open(CONFIG_FILE, 'r') as fh:
        config = load(fh)

    url = config['webhook_url']
    message = ' '.join(argv[1:])
    if not message:
        print(f'Usage: {argv[0]} message...')

    app_message = {
        'text': message,
    }
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(app_message),
    )


if __name__ == '__main__':
    main()
