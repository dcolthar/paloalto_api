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
        parser.add_argument('-k', '--key', help='pass an api key instead of authenticating with username/password')
        parser.add_argument('-u', '--username', help='if not passing a key, enter a username to use')
        parser.add_argument('-i', '--ip', help='the ip of the host to connect to, '
                                               'will default to 127.0.0.1 with no input!')
        parser.add_argument('-r', '--vrouter', help='the virtual router to use for lookup, default is DEFAULT VR')
        args = parser.parse_args()

        # If the hostname arg was passed, otherwise its going to 127.0.0.1 so will fail
        if args.ip:
            self.host = args.ip
            print('connecting to host {ip}'.format(ip=self.host))
        else:
            print('connecting to host 127.0.0.1')
            self.host = '127.0.0.1'

        # If debug is set to 1, then additional print output will be performed
        if args.debug:
            self.debug = args.debug
            print('debug level set to {level}'.format(level=args.debug))
        else:
            self.debug = 0

        # If vrouter arg was passed, otherwise set to default of DEFAULT VR
        if args.vrouter:
            self.vrouter = args.vrouter
            print('vrouter to use is {vrouter}'.format(vrouter=self.vrouter))
        else:
            print('vrouter to use is \'DEFAULT VR\'')
            self.vrouter = 'DEFAULT VR'

        # If username was passed we will assign that to the username global variable, otherwise set to admin
        if args.username:
            self.username = args.username
            print('set username to {username}'.format(username=args.username))
        else:
            print('set username to admin')
            self.username = 'admin'

        # If a key was used we don't need to prompt for a username and password
        if args.key:
            self.key = args.key
            print('we got a key passed to us so using that instead of username/password prompt')
        else:
            self.key = ''

        # Dictionary to hold IP key to zone value
        self.results = {}


    def getCredentials(self):
        '''
        Only if we don't pass an api key into the call we need to get it from the firewall
        :return:
        '''
        # If we already have the key, no need to perform this
        if not self.key:
            self.password = getpass.getpass('Enter the password for username {user}:\n'.format(user=self.username))

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
            # Lets try to connect
            try:
                r = requests.get(getKeyURL, verify=False)
                # The result data is put into the object data
                data = r.text

                # parse the xml to get a key using beatifulsoup that we imported for use
                soup = BS(data, "html.parser")
                # assign the value of the key to self.key
                self.key = str(soup.find('key').text)
            # Catch the connection error first then any other after it
            except requests.ConnectionError:
                print('Failed to connect to the host at {ip}'.format(ip=self.host))
                sys.exit(1)
            except Exception as e:
                print('An unknown error occurred when trying to connect to get the API key')
                sys.exit(2)


    def getSystemInfo(self):
        '''
        Simple query to pull system info from the firewall
        :return: newdata - a json object of the system results from the API query
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
            # Lets try to connect
            try:
                r = requests.get(getSystemInfoURL, verify=False)
                # The result data is put into the object data
                data = r.text

                # Convert the xml to json, then print it out all perdy like
                newdata = json.loads(json.dumps(xmltodict.parse(data)))
                if self.debug == 1:
                    print(json.dumps(newdata, indent=2, sort_keys=True))
                return newdata
            # Catch the connection error first then any other after it
            except requests.ConnectionError:
                print('Failed to connect to the host at {ip}'.format(ip=self.host))
                sys.exit(1)
            except Exception as e:
                print('An unknown error occurred when trying to connect to get system info')
                sys.exit(2)


    def testRouteLookup(self):
        '''
        Takes an ip and finds the output interface then calls interfaceToZone to resolve
        interface to zone name for the ip
        :return: self.results - a dictionary of all the ip to zone mapping, the ip is the key zone the value
        '''
        # run against a group of routes to check at once
        iplist = ['10.92.53.39', '10.96.5.19']
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
                    host=self.host, vrouter=self.vrouter, ip=ip, key=self.key
                )
                # Try to connect now
                try:
                    r = requests.get(testRouteLookupURL, verify=False)
                    # The result data is put into the object data
                    data = r.text

                    # Convert the xml to json, then print it out all perdy like
                    newdata = json.loads(json.dumps(xmltodict.parse(data)))

                    # If debugging print out all output
                    if self.debug == '1':
                        print(json.dumps(newdata, indent=2, sort_keys=True))

                    # This will assign the interface from the results
                    if self.debug == 1:
                        print(newdata)
                    interface = newdata['response']['result']['interface']

                    # now we will resolve the interface to zone name by calling interfaceToZone
                    zone = self.interfaceToZone(interface=interface)

                    # add the ip and zone to the results dictionary
                    self.results[ip] = zone

                    if self.debug == 1:
                        print('The host {ip} is out interface {interface} in zone {zone}'.format(
                            ip=ip, interface=interface, zone=zone
                        ))
                # Catch the connection error first then any other after it
                except requests.ConnectionError:
                    print('Failed to connect to the host at {ip} to perform a FIB lookup for '
                          'ip {iptolookup}'.format(ip=self.host, iptolookup=ip))
                    continue
                except Exception as e:
                    print('An unknown error occurred when trying to do a FIB lookup for ip {ip}'.format(ip=ip))
                    continue

            # Return the results dictionary
            return self.results

    def interfaceToZone(self, interface=''):
        '''
        takes an interface name from a call and returns the zone name
        :param interface:
        :return: zone - the zone the interface that was provided is mapped to
        '''
        # If we don't have the key, no point to continue
        if not self.key:
            print('We don\'t have an API key so the call will fail')
            sys.exit(1)
        else:
            if not interface:
                print('You didn\'t pass me an interface name')
                sys.exit(1)
            # If we got here we were passed an interface and should be good to get the zone mapping
            else:
                interfaceToZoneURL = \
                'https://{host}/api/?type=op&cmd=<show><interface>{interface}</interface></show>&key={key}'.format(
                    host=self.host, interface=interface, key=self.key
                )
                # Lets try to connect now
                try:
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
                # Catch the connection error first then any other after it
                except requests.ConnectionError:
                    print('Failed to connect to the host at {ip} to perform an interface to zone lookup')
                except Exception as e:
                    print('An unknown error occurred when trying to do an interface to zone lookup')





iptozone = IPtoZone()
iptozone.getCredentials()
iptozone.getKey()
print(iptozone.key)
#iptozone.getSystemInfo()
results = iptozone.testRouteLookup()
print(results)