# This class will simply return system info on the firewall

import requests
import json
import xmltodict
import sys
# Only do the urllib3 setting if you don't want to see any output about unverified HTTPS
# connections being made for things like self signed certs.  This effectively shuts up
# the warning.  Re-enable this if an environment is being used where the error shouldn't happen.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GetSystemInfo():

    def __init__(self, **kwargs):
        if kwargs is not None:
            kwargs_list = kwargs

        self.host = kwargs_list['host']
        self.key = kwargs_list['key']

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

                # return the newdata object containing the system info
                return newdata

            # Catch the connection error first then any other after it
            except requests.ConnectionError:
                print('Failed to connect to the host at {ip}'.format(ip=self.host))
                sys.exit(1)
            except Exception as e:
                print('An unknown error occurred when trying to connect to get system info')
                sys.exit(2)
