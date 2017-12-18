import requests
import getpass
import sys
import argparse
# Beautiful soup is used to scrape the XML to get values needed
from bs4 import BeautifulSoup as BS
# We import xmltodict and json to do some formatting of the output from the calls
import xmltodict
import json
# Only do the urllib3 setting if you don't want to see any output about unverified HTTPS
# connections being made for things like self signed certs.  This effectively shuts up
# the warning.  Re-enable this if an environment is being used where the error shouldn't happen.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



class IPtoZone():

    def __init__(self):

        # Lets get arguments passed in if any
        parser = argparse.ArgumentParser(description='Map IP Routes to Zones on PaloAlto firewalls')
        parser.add_argument('-d', '--debug', choices=['0','1'],
                            help='set debug level, 0 is default 1 is debug on')
        parser.add_argument('-k', '--key', help='pass an api key instead of authenticating')
        parser.add_argument('-u', '--username', help='if not passing a key, enter a username to use')
        parser.add_argument('-i', '--ip', help='the ip of the host to connect to, '
                                               'will default to 127.0.0.1 with no input!')
        args = parser.parse_args()

        # If the hostname arg was passed, otherwise its going to 127.0.0.1 so will fail
        if args.ip:
            self.host = args.ip
            print('connecting to host {ip}'.format(ip=self.host))
        else:
            self.host = '127.0.0.1'

        # If debug is set to 1, then additional print output will be performed
        if args.debug:
            self.debug = args.debug
            print('debug level set to {level}'.format(level=args.debug))

        # If username was passed we will assign that to the username global variable, otherwise set to admin
        if args.username:
            self.username = args.username
            print('set username to {username}'.format(username=args.username))
        else:
            self.username = 'admin'


        self.key = ''


    def getCredentials(self):
        '''
        Only if we don't pass an api key into the call we need to get it from the firewall
        :return:
        '''
        # If we already have the key, no need to perform this
        if not self.key:
            self.password = getpass.getpass()

    def getKey(self):
        '''
        getKey will get an API key if one is not provided for the username/password combo
        :return:
        '''
        if not self.key:
            # If we didn't get an api key from another method we need to obtain one
            # The below URL will be called to get this
            getKeyURL = 'https://{host}/api/?type=keygen&user={user}&password={password}'.format(
                host=self.host, user=self.username, password=self.password
            )
            r = requests.get(getKeyURL, verify=False)
            # The result data is put into the object data
            data = r.text

            # parse the xml to get a key
            soup = BS(data, "html.parser")
            # assign the value of the key to self.key
            self.key = str(soup.find('key').text)


    def getSystemInfo(self):
        '''
        Simple query to pull system info from the firewall
        :return:
        '''
        # If we don't have the key, no point to continue
        if not self.key:
            print('We don\'t have an API key so the call will fail')
            sys.exit(1)
        else:
            # The full URL to call to get systeminfo
            getSystemInfoURL = \
                'https://{host}/api/?type=op&cmd=<show><system><info></info></system></show>&key={key}'.format(
                    host=self.host, key=self.key
                )
            r = requests.get(getSystemInfoURL, verify=False)
            # The result data is put into the object data
            data = r.text

            # Convert the xml to json, then print it out all perdy like
            newdata = json.loads(json.dumps(xmltodict.parse(data)))
            print(json.dumps(newdata, indent=2, sort_keys=True))


    def testRouteLookup(self):
        '''
        Takes an ip and finds the output interface then calls interfaceToZone to resolve
        interface to zone name for the ip
        :return:
        '''
        # run against a group of routes to check at once
        iplist = ['172.16.40.1', '172.16.1.1', '8.8.8.8']
        vrouter = 'DEFAULT VR'
        # If we don't have the key, no point to continue
        if not self.key:
            print('We don\'t have an API key so the call will fail')
            sys.exit(1)
        else:
            for i in iplist:
                ip = i
                # The full URL to call to get the route info
                testRouteLookupURL = \
                'https://{host}/api/?type=op&cmd=<test><routing><fib-lookup>' \
                '<virtual-router>{vrouter}</virtual-router><ip>{ip}</ip></fib-lookup></routing></test>' \
                '&key={key}'.format(
                    host=self.host, vrouter=vrouter, ip=ip, key=self.key
                )
                r = requests.get(testRouteLookupURL, verify=False)
                # The result data is put into the object data
                data = r.text

                # Convert the xml to json, then print it out all perdy like
                newdata = json.loads(json.dumps(xmltodict.parse(data)))

                # If debugging print out all output
                if self.debug == '1':
                    print(json.dumps(newdata, indent=2, sort_keys=True))

                # This will assign the interface from the results
                interface = newdata['response']['result']['interface']

                # now we will resolve the interface to zone name by calling interfaceToZone
                zone = self.interfaceToZone(interface=interface)

                print('The host {ip} is out interface {interface} in zone {zone}'.format(
                    ip=ip, interface=interface, zone=zone
                ))

    def interfaceToZone(self, interface=''):
        '''
        takes an interface name from a call and returns the zone name
        :param interface:
        :return:
        '''
        # If we don't have the key, no point to continue
        if not self.key:
            print('We don\'t have an API key so the call will fail')
            sys.exit(1)
        else:
            if not interface:
                print('You didn\'t pass me an interface name')
                sys.exit(1)
            else:
                interfaceToZoneURL = \
                'https://{host}/api/?type=op&cmd=<show><interface>{interface}</interface></show>&key={key}'.format(
                    host=self.host, interface=interface, key=self.key
                )
                r= requests.get(interfaceToZoneURL, verify=False)
                data = r.text

                # Convert the xml to json, then print it out all perdy like
                newdata = json.loads(json.dumps(xmltodict.parse(data)))

                # If debugging print out all output
                if self.debug == '1':
                    print(json.dumps(newdata, indent=2, sort_keys=True))

                # This will assign the zone from the results
                zone = newdata['response']['result']['ifnet']['zone']

                # return the zone
                return zone





iptozone = IPtoZone()
iptozone.getCredentials()
iptozone.getKey()
print(iptozone.key)
#iptozone.getSystemInfo()
iptozone.testRouteLookup()