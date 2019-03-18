#!python
class Barcode(object):
    """Abstract BC, shared by both EAN and UCC BCs"""
    def __init__(self):
        name = ''
        self.digits = ["3211","2221","2122","1411","1132","1231","1114","1312","1213","3112"]    
        self.mirror = [ "------","--1-11","--11-1","--111-","-1--11","-11--1","-111--","-1-1-1","-1-11-","-11-1-"]         
        self.guards = {'normal': '-111--', 'centre': '11111-', 'special':'111111','add_on':'-112--', 'deliniator':'11----'}
    
    
    def encoding_a(self,i):
        #print 'encoding %s' % i
        letter = self.digits[i]
        pos0 = '0' * int(letter[0])         
        pos1 = '1' * int(letter[1])        
        pos2 = '0' * int(letter[2])        
        pos3 = '1' * int(letter[3])        
        s = ''.join([pos0,pos1,pos2,pos3])
        self.data.append((i, s, 'a'))
        return
    

    def encoding_b(self,i):
        #print 'encoding %s' % i
        letter = self.digits[i]
        pos0 = '0' * int(letter[3])         
        pos1 = '1' * int(letter[2])        
        pos2 = '0' * int(letter[1])        
        pos3 = '1' * int(letter[0])        
        s = ''.join([pos0,pos1,pos2,pos3])
        self.data.append((i, s, 'b'))        
    

    def encoding_c(self,i):
        #print 'encoding %s' % i
        letter = self.digits[i]
        pos0 = '1' * int(letter[0])         
        pos1 = '0' * int(letter[1])        
        pos2 = '1' * int(letter[2])        
        pos3 = '0' * int(letter[3])        
        s = ''.join([pos0,pos1,pos2,pos3])
        self.data.append((i, s, 'c'))
    

    def encoding_guard(self, name):
        #print 'encoding %s' % i
        guard_pattern = self.guards[name]
        image = '010101'
        guard = ''
        i = -1
        for s in guard_pattern:
            i += 1
            if s == '-': 
                continue
            else:
                guard += image[i] * int(s)
        self.data.append(('g', guard, ''))        
    

class EAN13(Barcode):
    def __init__(self, arg):
        name = 'EAN13'
        QZONE_LEFT  = 11
        QZONE_RIGHT = 7
        
        Barcode.__init__(self)
        self.arg = arg
        self.data = []
        
        assert len(self.arg) == 13
        
        digs = [int(c) for c in arg]
        m = self.mirror[digs[0]]
        #add left quiet zone
        self.data.append(('q','0' * QZONE_LEFT, ''))
        #add left guard
        self.encoding_guard('normal')
        #process left digits
        for i in range(1,7):            
            if m[i-1] == '1':
                self.encoding_b(digs[i])
            else:
                self.encoding_a(digs[i])
        #add centre guard
        self.encoding_guard('centre')
        #process right digits
        for i in range(7,13):
            self.encoding_c(digs[i])
        #add right guard
        self.encoding_guard('normal')
        #add right quiet zone
        self.data.append(('q','0' * QZONE_RIGHT, ''))
    

class UPCA(Barcode):
    def __init__(self, arg):
        name = 'UPCA'
        QZONE_LEFT  = 9
        QZONE_RIGHT = 9

        Barcode.__init__(self)
        self.arg = '0' + arg
        self.data = []
        
        #print self.arg
        #assert len(self.arg) == 13
        
        digs = [int(c) for c in self.arg]
        m = self.mirror[digs[0]]
        #add left quiet zone
        self.data.append(('q','0' * QZONE_LEFT, ''))
        #add left guard
        self.encoding_guard('normal')
        #process left digits
        for i in range(1,7):            
            self.encoding_a(digs[i])
        #add centre guard
        self.encoding_guard('centre')
        #process right digits
        for i in range(7,13):
            self.encoding_c(digs[i])
        #add right guard
        self.encoding_guard('normal')
        #add right quiet zone
        self.data.append(('q','0' * QZONE_RIGHT, ''))
        
# def _main_ean(s):
#     ean13 = EAN13(s)
#     print ean13.data
        
# def _main_upc(s):
#     upc = UPCA(s)
#     print upc.data
        
# if __name__ == '__main__':
#     _main_ean('6001240720288')
#     _main_upc('075678164125')
