#!/usr/local/bin/python
from .BarcodeManager import EAN13

class ISBNHelper:
    """
    >>> ISBNHelper('9780140150988').getHyphens()
    'ISBN 978-0-14-015098-8'

    >>> ISBNHelper('9792222222223').getHyphens()
    False

    >>> ISBNHelper('9780072125757').getHyphens()
    'ISBN 978-0-07-212575-7'

    """

    def prefix_array(self,su,sl):
        pl = len(su)
        assert pl == len(sl)
        return [str(i).zfill(pl) for i in range(int(su),int(sl) + 1)]

    def split_isbn(self,i1,i2):
        part0 = self.arg[0:3]
        part1 = self.arg[3:3+i1]
        part2 = self.arg[3+i1:3+i2]
        part3 = self.arg[3+i2:-1]
        part4 = self.arg[-1]
        assert self.arg == "%s%s%s%s%s" % (part0,part1,part2,part3,part4)
        return "ISBN %s-%s-%s-%s-%s" % (part0,part1,part2,part3,part4)

    def hyphenate(self, gd):
        branch = self.HYPHEN_TABLE[int(gd)]
        for k in branch.keys():
            su,sl = k.split('-')
            for prefix in self.prefix_array(su, sl):
                if self.arg[4:].find(prefix) == 0:
                    #print su, sl, prefix, branch[k]
                    return self.split_isbn(len(gd),branch[k])
        return False

    def __init__(self, arg):
        self.COUNTRY = {}

        self.HYPHEN_TABLE = {
            0: {"00-19":3,
                "20-69":4,
                "70-84":5,
                "85-89":6,
                "90-94":7,
                "95-99":8},

            1: {"10-39":  4,
                "40-54":  5,
                "5500-8697":6,
                "8698-9989":7,
                "9990-9999":8}
        }
        #assert utils.isValid(arg)
        self.arg = arg

    def getHyphens(self):
        gd = self.arg[3]
        if int(gd) < 2:
            return self.hyphenate(gd)
        else:
            return False


class ISBN13(EAN13):
    """This class just inherits EAN13"""
    def __init__(self, arg):
        EAN13.__init__(self,arg)
        name = 'ISBN13'

class ISBN13AddOn(EAN13):
    """
    >>> a = ISBN13AddOn('9780072125757','50000')
    >>> a.arg
    '9780072125757'
    >>> a.add_on
    '50000'
    >>> a.data
    [('q', '00000000000', ''), ('g', '101', ''), (7, '0111011', 'a'), (8, '0001001', 'b'), (0, '0100111', 'b'), (0, '0001101', 'a'), (7, '0010001', 'b'), (2, '0010011', 'a'), ('g', '01010', ''), (1, '1100110', 'c'), (2, '1101100', 'c'), (5, '1001110', 'c'), (7, '1000100', 'c'), (5, '1001110', 'c'), (7, '1000100', 'c'), ('g', '101', ''), ('q', '0000000', ''), ('q', '00', ''), ('g', '1011', ''), (5, '0110001', 'a'), ('g', '01', ''), (0, '0001101', 'a'), ('g', '01', ''), (0, '0100111', 'b'), ('g', '01', ''), (0, '0100111', 'b'), ('g', '01', ''), (0, '0001101', 'a'), ('q', '00000', '')]
    """
    def get_V(self,s):
        a = (int(s[0]) + int(s[2]) + int(s[4])) * 3
        b = (int(s[1]) + int(s[3])) * 9
        c = a + b
        return int(('%s' % c)[-1])
    def __init__(self, arg, add_on):
        EAN13.__init__(self,arg)
        name = 'ISBN13ADDON'
        #self.arg = arg
        self.add_on = add_on
        self.add_on_five = {0:'BBAAA', 1:'BABAA', 2:'BAABA', 3:'BAAAB', 4:'ABBAA',
        5:'AABBA', 6:'AAABB', 7:'ABABA', 8:'ABAAB', 9:'AABAB'}
        #add on five digits
        #opening qzone
        self.data.append(('q','0' * 2, '')) #add two white lines more thuse increasing qzone between main symbol and addon to 7

        self.encoding_guard('add_on')
        v = self.get_V(add_on)
        i = 0
        for c in self.add_on_five[v]:
            if i: self.encoding_guard('deliniator') #all except the first
            if c == 'A': self.encoding_a(int(add_on[i]))
            if c == 'B': self.encoding_b(int(add_on[i]))
            i += 1
        #closing qzone
        self.data.append(('q','0' * 5, ''))

