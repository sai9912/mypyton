class AbstractITF14Barcode(object):
    """Abstract BC, shared by both EAN and UCC BCs"""
    def __init__(self):
        name = ''
        self.digits = [ "00110","10001","01001","11000","00101",
                        "10100","01100","00011","10010","01010"]
        self.guards = {'start': '0-0-', 'stop': '1-0'}


    def get_bar_width(self,s):
        if s == '0':
            return 2
        if s == '1':
            return 5

    def encoding_pair(self,i,j):
        #print 'encoding %s' % i
        letter_i = self.digits[i]
        letter_j = self.digits[j]
        pos = []
        for x in range(5):
            pos.append(self.get_bar_width(letter_i[x])*'1') #dark first
            pos.append(self.get_bar_width(letter_j[x])*'0') #light after
        s = ''.join(pos)
        self.data.append((10*i + j, s, 'a'))
        return

    def encoding_guard(self, name):
        #print 'encoding %s'
        if name == 'start':
            self.data.append(('g', '11001100', ''))
        if name == 'stop':
            self.data.append(('g', '111110011', ''))


class ITF14(AbstractITF14Barcode):
    def __init__(self, arg):
        name = 'ITF14'
        QZONE_LEFT  = 10
        QZONE_RIGHT = 10

        AbstractITF14Barcode.__init__(self)
        self.arg = arg
        self.data = []

        digs = [int(c) for c in arg]

        #add left quiet zone
        self.data.append(('q','00' * QZONE_LEFT, '')) #ten times narrow
        #add left guard
        self.encoding_guard('start')

        #process digits
        for i in range(int(len(arg)/2)):
            c = 2 * i
            self.encoding_pair(digs[c],digs[c+1])

        #add right guard
        self.encoding_guard('stop')
        #add right quiet zone
        self.data.append(('q','00' * QZONE_RIGHT, ''))
