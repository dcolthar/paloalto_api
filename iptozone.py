import requests
import getpass
import sys
import argparse
# Beautiful soup is used to scrape the XML to get values needed
from bs4 import BeautifulSoup as BS
# We import xmltodict and json to do some formatting of the output from the calls
import xmltodict
import json




class IPtoZone():

    def __init__(self, **kwargs):
        # Dictionary to hold IP key to zone value
        self.results = {}

        if kwargs is not None:
            kwargs_list = kwargs

        self.host = kwargs_list['host']
        self.key = kwargs_list['key']
        self.vrouter = kwargs_list['vrouter']
        self.debug = kwargs_list['debug']


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