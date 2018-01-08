# This class is just used to look through a file, find things that look like IP addresses and put them in a list
import re

class ReadToIPList():

    def __init__(self, **kwargs):
        if kwargs is not None:
            kwargs_list = kwargs

        if kwargs_list['ipaddressfile']:
            self.file = kwargs_list['ipaddressfile']
        else:
            # if a file wasn't passed in default to iplist.txt
            self.file = 'iplist.txt'
        # list of IPs to store
        self.iplist = []
        # simple regex pattern to see if the item in the list is an ip address
        self.pattern = re.compile('([0-9]{1,3}\.){3}[0-9]{1,3}')


    def doWork(self):
        '''
        Parses the file, adds to a list then returns the list
        :return: self.iplist - list of IPs in python list format
        '''
        with open (self.file, 'r') as infile:
            for i in infile:
                if self.pattern.match(i):
                    self.iplist.append(i.rstrip())
            return self.iplist