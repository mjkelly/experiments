import json
import subprocess
import os
#import git

def main_handler(event, context):
    messages = []
    print 'main_handler called: %s' % event
    task_root = os.getenv('LAMBDA_TASK_ROOT')
    git = os.path.join(task_root, 'amzn-git')
    if os.path.isfile(git):
        messages.append("%s exists" % git)

    try:
        output = subprocess.check_output(['ls', task_root])
        messages.append('ls output: %s' % output)
    except Exception as e:
        messages.append("got exception: %s" % e)

    #try:
        #output = subprocess.check_output(['ls', '-l', git])
        #messages.append('ls -l output: %s' % output)
    #except Exception as e:
        #messages.append("got exception: %s" % e)

    #git_output = ''
    #try:
        #git_output = subprocess.check_output(
            #['bash', '-c', '%s help' % git],
            #stderr=subprocess.STDOUT)
    #except subprocess.CalledProcessError as e:
        #messages.append("got exception: %s" % e)
        #messages.append("e.output: %s" % e.output)

    # When we're invoked as a webhook, all the data is in the 'body' attribute.
    # It's easier to test by just invoking the lambda directly, though, so we
    # support both ways.
    is_webhook = 'body' in event

    if is_webhook:
        data = json.loads(event['body'])
    else:
        data = event

    print 'keys:'
    for k in data.keys():
        print '    %s' % k
    
    #try:
        #print "SENDER: %s" % data['sender']
        #print "LOGIN: %s" % data['sender']['login']
        #message = 'Hello %s!' % data['sender']['login']
    #except KeyError:
        #message = 'Hello anonymous user'
    
    body = {
        'messages': messages,
    }
    if is_webhook:
        return { 
            'statusCode': 200,
            'body': json.dumps(body),
        }
    else:
        return body
