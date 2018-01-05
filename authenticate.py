# This class handles authentication such as getting password and getting api key

import getpass
import requests
import sys
# Beautiful soup is used to scrape the XML to get values needed
from bs4 import BeautifulSoup as BS
# Only do the urllib3 setting if you don't want to see any output about unverified HTTPS
# connections being made for things like self signed certs.  This effectively shuts up
# the warning.  Re-enable this if an environment is being used where the error shouldn't happen.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)




class Authenticate():

    def __init__(self, **kwargs):
        if kwargs is not None:
            kwargs_list = kwargs

        self.host = kwargs_list['host']
        self.username = kwargs_list['username']
        self.password = ''

    def getCredentials(self):
        '''
        Only if we don't pass an api key into the call we need to get it from the firewall
        :return:
        '''
        self.password = getpass.getpass('Enter the password for username {user}:\n'.format(user=self.username))

    def getKey(self):
        '''
        getKey will get an API key if one is not provided for the username/password combo
        :return: self.key  - the api key for future use
        '''
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

            # return the api key
            return self.key

        # Catch the connection error first then any other after it
        except requests.ConnectionError:
            print('Failed to connect to the host at {ip}'.format(ip=self.host))
            sys.exit(1)
        except Exception as e:
            print('An unknown error occurred when trying to connect to get the API key')
            sys.exit(2)
