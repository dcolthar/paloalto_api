# Main class

import iptozone
import getsysteminfo
import authenticate
import check_for_pending_commit
import argparse
import json



class Main():

    def __init__(self):
        # Lets get arguments passed in if any
        parser = argparse.ArgumentParser(description='Map IP Routes to Zones on PaloAlto firewalls')
        parser.add_argument('-d', '--debug', choices=['0', '1'],
                            help='set debug level, 0 is default 1 is debug on')
        parser.add_argument('-k', '--key', help='pass an api key instead of authenticating with username/password')
        parser.add_argument('-u', '--username', help='if not passing a key, enter a username to use')
        parser.add_argument('-i', '--ip', help='the ip of the host to connect to, '
                                               'will default to 127.0.0.1 with no input!')
        parser.add_argument('-r', '--vrouter', help='the virtual router to use for lookup, default is DEFAULT VR')
        parser.add_argument('-a', '--action', help='the action to take', choices=['iptozone', 'getsysteminfo',
                                                                                  'testing'])
        parser.add_argument('-c', '--checkcommit', help='will check for pending commits', choices=['yes', 'no'])
        parser.add_argument('-f', '--ipaddressfile', help='ip address file to use')
        args = parser.parse_args()

        # summary of work is an output of all the varibles set on the call, to be output if debug=1
        summary_of_work = {}

        # If debug is set to 1, then additional print output will be performed
        if args.debug:
            self.debug = args.debug
            summary_of_work['debuglevel'] = '1, debugging enabled'
        else:
            self.debug = 0

        # If the hostname arg was passed, otherwise its going to 127.0.0.1 so will fail
        if args.ip:
            self.host = args.ip
            summary_of_work['ip'] = 'connecting to host {ip}'.format(ip=self.host)
        else:
            self.host = '127.0.0.1'
            summary_of_work['ip'] = 'connecting to host 127.0.0.1'


        # If vrouter arg was passed, otherwise set to default of DEFAULT VR
        if args.vrouter:
            self.vrouter = args.vrouter
            summary_of_work['vrouter'] = 'vrouter to use is {vrouter}'.format(vrouter=self.vrouter)
        else:
            self.vrouter = 'DEFAULT VR'
            summary_of_work['vrouter'] = 'vrouter to use is \'DEFAULT VR\''

        # If username was passed we will assign that to the username global variable, otherwise set to admin
        if args.username and not args.key:
            self.username = args.username
            summary_of_work['username'] = 'set username to {username}'.format(username=self.username)
        elif not args.key:
            self.username = 'admin'
            summary_of_work['username'] = 'set username to admin'

        # If an action was chosen we assign to self.action otherwise set default to getsysteminfo
        if args.action:
            self.action = args.action
            summary_of_work['action'] = 'performing the action {action}'.format(action=self.action)
        else:
            self.action = 'getsysteminfo'
            summary_of_work['action'] = 'no action passed explicitly so set to getsysteminfo'

        # If we pass a file of ip addresses set it here, this is used for things like ip to zone lookup, etc
        if args.ipaddressfile:
            self.ipaddressfile = args.ipaddressfile
            summary_of_work['ipaddressfile'] = 'passed an IP address file in, filename is {file}'.format(
                file=self.ipaddressfile
            )


        # If a key was used we don't need to prompt for a username and password
        if args.key:
            self.key = args.key
            summary_of_work['key'] = self.key
            # At the end of the work and variables so call debug output method
            self.debugOutput(summary_of_work)
        else:
            summary_of_work['key'] = 'key was not provided and was gained through username/password auth'
            # We will call this before trying to get key just in case we fail connection then debug
            # will still output info that is helpful
            self.debugOutput(summary_of_work)
            auth = authenticate.Authenticate(host=self.host, username=self.username)
            auth.getCredentials()
            self.key = auth.getKey()
            print('api key for future use is:\n{key}\n'.format(key=self.key))

        # Check if we should look for pending changes
        if args.checkcommit == 'yes':
            self.checkCommit()



    def debugOutput(self, summary_of_work):
        if self.debug == '1':
            for k, v in summary_of_work.items():
                print('{key} : {value}'.format(key=k, value=v))

    def actionSwitch(self):
        if self.action == 'testing':
            print('\n reserved for testing \n')

        elif self.action == 'getsysteminfo':
            sysinfo = getsysteminfo.GetSystemInfo(host=self.host, key=self.key)
            results = sysinfo.getSystemInfo()
            print(json.dumps(results, indent=2, sort_keys=True))

        elif self.action == 'iptozone':
            tozone = iptozone.IPtoZone(host=self.host, debug=self.debug, key=self.key, vrouter=self.vrouter)
            results = tozone.testRouteLookup()
            print(json.dumps(results, indent=2, sort_keys=True))

    def checkCommit(self):
        '''
        Creates an instance of the CheckForCommit class in check_for_pending_commit.py
        :return:
        '''
        check_commit = check_for_pending_commit.CheckForCommit(host=self.host, key=self.key)
        commit_status = check_commit.checkForCommit()
        if commit_status == True:
            changes = check_commit.showPendingChanges()
            print('Changes are pending commit:')
            print(json.dumps(changes, indent=2, sort_keys=True))
        if commit_status == False:
            print('No changes are pending commit')





if __name__ == '__main__':
    main = Main()
    # run to see what action to execute
    main.actionSwitch()

