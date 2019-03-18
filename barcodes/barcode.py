from  .symbologies import name, name2, description, literal
from  .utilities import getValid

class Barcode(object):
    """docstring for Barcode
    >>> Barcode('6001240720288').ean13
    True
    >>> Barcode('075678164125').upc12
    True
    >>> Barcode('0075678164125').upc12
    True
    >>> Barcode('00075678164125').itf14
    True
    >>> Barcode('040000000006').upc12
    True
    >>> Barcode('050000000005').upc12
    True

    """
    def __init__(self, data):
        self.data = data
        self.length = len(data)
        self.data14 = ''
        self.kind = ''
        self.prefix = ''
        self.upc12 = False #can it be represented as 12d?
        self.ean13 = False #can it be represented as 13d?
        self.itf14 = False #can it be represented as 14d?
        self.valid = False
        self.vars = {}
        self.images = {}
        self.symbols = {}
        self.primary_encoding = None
        self.name = None
        self.name2 = None
        self.literal = None
        self.description = None
        self.area_of_application = None
        self.gcp = None
        self.packaging = None
        self.item_reference = None
        self.previous   = None
        self.next       = None
        self.previous_h  = None
        self.next_h     = None
        self.this_h     = None
        self.prefix     = None
        self.capacity   = None
                
        self.analyse()
        if self.valid:
            self.set_variations()
    
    def analyse(self):
        if self.length == 12:
            self.prefix = '0%s' % self.data[0:2]
            self.upc12 = True
            self.ean13 = True
            self.itf14 = True
            self.data12 = self.data
            self.data13 = '0'  + self.data            
            self.data14 = '00' + self.data
            self.primary_encoding = 'upc-a'
            self.valid = self.isValid(self.data)

        if self.length == 13:
            self.prefix = self.data[0:3]
            if self.prefix[0] == '0': 
                self.upc12 = True
                self.data12 = self.data[1:]
                
            self.ean13 = True
            self.data13 = self.data

            self.itf14 = True
            self.data14 = '0' + self.data

            self.primary_encoding = 'ean-13'
            self.valid = self.isValid(self.data)
            
        if self.length == 14:
            self.prefix = self.data[1:4]
            if self.prefix[0] == '0': 
                self.upc12 = True
                self.data12 = self.data[2:]
                
            if self.data[0] == '0': 
                self.ean13 = True
                self.data13 = self.data[1:]
                
            self.itf14 = True
            self.data14 = self.data
            
            self.primary_encoding = 'itf-14'
            self.valid = self.isValid(self.data)
        
        #calculate previous and next barcodes
        if self.valid and int(self.data) > 10:
            
            _current    = int(self.data)
            _previous   = str(_current - 10)
            _next       = str(_current + 10)
            self.previous = getValid(_previous).zfill(self.length)
            self.next     = getValid(_next).zfill(self.length)
            self.previous_h = self.previous
            self.this_h     = self.data
            self.next_h     = self.next
            
        
        #calculate company prefix
        if self.data14:
            self.gcp            = self.data14[1:7]
            self.item_reference = self.data14[7:-1]
            self.packaging      = self.data14[0]
        
        #get area of application
        if self.upc12:
            a = int(self.data12[1])
            #0,	Regular UPC codes
            #1,	Reserved
            #2,	Weight items marked at the store
            #3,	National Drug/Health-related code
            #4,	No format restrictions, in-store use on non-food items
            #5,	Coupons
            #6,	Reserved
            #7,	Regular UPC codes
            #8,	Reserved
            #9,	Reserved
            if a in (0,7):
                self.area_of_application = "Regular UPC codes"
            if a in (1,6,8,9):
                self.area_of_application = "Reserved"
            if a == 2:
                self.area_of_application = "Weight items marked at the store"
            if a == 3:
                self.area_of_application = "National Drug/Health-related code"
            if a == 4:
                self.area_of_application = "No format restrictions, in-store use on non-food items"
            if a == 5:
                self.area_of_application = "Coupons"
            
            
    def set_variations(self):
        if self.upc12:
            #self.vars['upc-a'] = self.data14[2:]
            self.symbols['upc-a'] = {}
            self.symbols['upc-a']['data'] = self.data14[2:]
            self.symbols['upc-a']['text'] =  description['upc-a']
            self.symbols['upc-a']['name'] =  name['upc-a']
            self.symbols['upc-a']['name2'] =  name2['upc-a']
            self.symbols['upc-a']['literal'] =  literal['upc-a']
            
        if self.ean13:
            #self.vars['ean-13'] = self.data14[1:]
            self.symbols['ean-13'] = {}
            self.symbols['ean-13']['data'] = self.data14[1:]
            self.symbols['ean-13']['text'] =  description['ean-13']        
            self.symbols['ean-13']['name'] =  name['ean-13']        
            self.symbols['ean-13']['name2'] =  name2['ean-13']
            self.symbols['ean-13']['literal'] =  literal['ean-13']

        if self.itf14:
            #self.vars['ean-13'] = self.data14[1:]
            self.symbols['itf-14'] = {}
            self.symbols['itf-14']['data'] = self.data14
            self.symbols['itf-14']['text'] =  description['itf-14']        
            self.symbols['itf-14']['name'] =  name['itf-14']        
            self.symbols['itf-14']['name2'] =  name2['itf-14']
            self.symbols['itf-14']['literal'] =  literal['itf-14']
            
        
    def isValid(self,nums):
         if len(nums) == 0: return False
         cd1  = nums[-1]
         meat = nums[0:-1][::-1]#cut cd away, reverse string, since x3 always applays from right (BC)
         odds = sum(map(lambda i: int(i)*3,list(meat[0::2])))
         evns = sum(map(lambda i: int(i),list(meat[1::2])))
         cd2  = str(10 - ((odds + evns) % 10))[-1]# 0 if 10 or reminder
         return cd1 == cd2
            
if __name__ == "__main__":  # pragma: no cover
    for s in ['6001240720288','075678164125','1', '', '1234567789', '0000000000000']:
        pass
        # print s
        # bc = Barcode(s)
        # print bc.length
        # print bc.prefix
        # print bc.symbols
        # print bc.valid
        # print bc.previous_h
        # print bc.this_h
        # print bc.next_h
        # print '---'
    
#from http://www.barcodeisland.com/upca.phtml    
        # 0	Regular UPC codes
        # 1	Reserved
        # 2	Weight items marked at the store
        # 3	National Drug/Health-related code
        # 4	No format restrictions, in-store use on non-food items
        # 5	Coupons
        # 6	Reserved
        # 7	Regular UPC codes
        # 8	Reserved
        # 9	Reserved
