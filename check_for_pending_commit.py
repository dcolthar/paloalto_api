# The purpose of this is to check to see if any pending changes exist
# if there is a pending commit then probably best to not go forward if doing config changes
import requests
import sys
import xmltodict
import json

class CheckForCommit():

    def __init__(self, host='127.0.0.1', key=None):
        # host is the host to connect to
        self.host = host
        # We'll never need the username because before calling this the user will have to authenticate
        # by passing a key or logging in
        self.key = key


    def checkForCommit(self):
        '''
        Checks to see if any changes are awaiting commit and returns a True is yes and False if no
        :return: commit_state - True or False
        '''
        if not self.key:
            print('We don\'t have an API key so the call will fail')
            sys.exit(1)

        url ='https://{host}/api/?type=op&cmd=<check><pending-changes></pending-changes></check>&key={key}'.format(
            host=self.host, key=self.key
        )
        # lets try to connect now
        r = requests.get(url, verify=False)
        data = r.text

        newdata = json.loads(json.dumps(xmltodict.parse(data)))

        # Print the result which is a 'yes' if changes are pending
        print(newdata['response']['result'])

        if newdata['response']['result'] == 'yes':
            commit_state = True
            # Try to get a summary of the changes that are awaiting commit
            changes = self.showPendingChanges()
            print(changes)
            return commit_state
        else:
            commit_state = False
            return commit_state

    def showPendingChanges(self):
        '''
        Will return pending changes so if there are changes you can view them
        :return: pending_changes
        '''
        url = 'https://{host}//api/?type=op&cmd=<show><config><list><changes></changes></list></config></show>' \
              '&key={key}'.format(host=self.host, key=self.key)
        # lets try to connect now
        r = requests.get(url, verify=False)
        data = r.text

        newdata = json.loads(json.dumps(xmltodict.parse(data)))
        print(newdata)