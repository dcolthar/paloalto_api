import re

class ReadToIPList():

    def __init__(self):
        self.file = 'iplist.txt'
        self.iplist = []
        self.pattern = re.compile('([0-9]{1,3}\.){3}[0-9]{1,3}')


    def doWork(self):
        with open (self.file, 'r') as infile:
            for i in infile:
                if self.pattern.match(i):
                    self.iplist.append(i.rstrip())

            print(self.iplist)



test = ReadToIPList()
test.doWork()