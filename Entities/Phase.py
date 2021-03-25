
# Import Section
import re, time
import Util as util
import jsons, json
from typing import List, Set, Tuple, Dict


# Super Class
from Entities.Entity import Entity


# Children Classes


#  Logging Support
import logging
logger = logging.getLogger(__name__)


class Phase (Entity):

    _id = 0
    suid = util.getID()
    loaded = False


    # Common / non Property / Private Variables ====================================================================
    owner = 'instance'
    index = int(0)
    parent = util.getID()
    

    # Children initial setup
    

    #  PROPERTIES ================================================================================================
    
    _phase_type = int(0)
    @property
    def phase_type(self):
        return self._phase_type

    @phase_type.setter
    def phase_type(self, new):
        self.notifyChange('phase_type', self._phase_type, new)
        self._phase_type = new


    _p0 = float(756.987)
    @property
    def p0(self):
        return self._p0

    @p0.setter
    def p0(self, new):
        self.notifyChange('p0', self._p0, new)
        self._p0 = new


    _recal_a0 = float(-64000)
    @property
    def recal_a0(self):
        return self._recal_a0

    @recal_a0.setter
    def recal_a0(self, new):
        self.notifyChange('recal_a0', self._recal_a0, new)
        self._recal_a0 = new


    _recal_a1 = float(1.091954E-03)
    @property
    def recal_a1(self):
        return self._recal_a1

    @recal_a1.setter
    def recal_a1(self, new):
        self.notifyChange('recal_a1', self._recal_a1, new)
        self._recal_a1 = new


    _poly1_a0 = float(0)
    @property
    def poly1_a0(self):
        return self._poly1_a0

    @poly1_a0.setter
    def poly1_a0(self, new):
        self.notifyChange('poly1_a0', self._poly1_a0, new)
        self._poly1_a0 = new


    _poly1_a1 = float(1)
    @property
    def poly1_a1(self):
        return self._poly1_a1

    @poly1_a1.setter
    def poly1_a1(self, new):
        self.notifyChange('poly1_a1', self._poly1_a1, new)
        self._poly1_a1 = new


    _poly1_a2 = float(0)
    @property
    def poly1_a2(self):
        return self._poly1_a2

    @poly1_a2.setter
    def poly1_a2(self, new):
        self.notifyChange('poly1_a2', self._poly1_a2, new)
        self._poly1_a2 = new


    _poly1_a3 = float(0)
    @property
    def poly1_a3(self):
        return self._poly1_a3

    @poly1_a3.setter
    def poly1_a3(self, new):
        self.notifyChange('poly1_a3', self._poly1_a3, new)
        self._poly1_a3 = new


    _poly2_a0 = float(0)
    @property
    def poly2_a0(self):
        return self._poly2_a0

    @poly2_a0.setter
    def poly2_a0(self, new):
        self.notifyChange('poly2_a0', self._poly2_a0, new)
        self._poly2_a0 = new


    _poly2_a1 = float(1)
    @property
    def poly2_a1(self):
        return self._poly2_a1

    @poly2_a1.setter
    def poly2_a1(self, new):
        self.notifyChange('poly2_a1', self._poly2_a1, new)
        self._poly2_a1 = new


    _poly2_a2 = float(0)
    @property
    def poly2_a2(self):
        return self._poly2_a2

    @poly2_a2.setter
    def poly2_a2(self, new):
        self.notifyChange('poly2_a2', self._poly2_a2, new)
        self._poly2_a2 = new


    _poly2_a3 = float(0)
    @property
    def poly2_a3(self):
        return self._poly2_a3

    @poly2_a3.setter
    def poly2_a3(self, new):
        self.notifyChange('poly2_a3', self._poly2_a3, new)
        self._poly2_a3 = new


    _xaxis = list()
    @property
    def xaxis(self):
        return self._xaxis

    @xaxis.setter
    def xaxis(self, new):
        self.notifyChange('xaxis', self._xaxis, new)
        self._xaxis = new


    _yaxis = list()
    @property
    def yaxis(self):
        return self._yaxis

    @yaxis.setter
    def yaxis(self, new):
        self.notifyChange('yaxis', self._yaxis, new)
        self._yaxis = new



    def __init__(self, qlog=None):
        self.loaded = False

        logger = self.configLogger()
        #logger.debug('Phase loaded'.format())

    def load (self, input ):
        
        #loadcode_begin

        #loadcode_end

        self.loaded = True

    def parse (self, sparse='', edata=''):
        
        #parsecode_begin
        pass
        #parsecode_end


    def loadDefault(self):
        
        #defaultcode_begin
        pass
        #defaultcode_end


    @classmethod
    def getInstance(cls, mongolink=None, store=True):

        instance = Phase()
        instance.suid= util.getID()
        if mongolink is not None:
            idx = mongolink.registerEntity({'instance':instance,
                                            'collection':'phase',
                                            'id':instance.suid,
                                            'query' : None,
                                            'tstamp' : util.getID(),
                                            'realm' : 'created'
                                            }, instance)
            instance._descriptor = idx
            
        return instance

    def toDict(self, embed=False):
        dumped = jsons.dumps(self, embed=embed, caller=self, strip_privates=True)
        jobj = json.loads(dumped)
        return jobj

    def getSerial(self):
        return self.suid


        






    #classcode_begin

    #classcode_end

