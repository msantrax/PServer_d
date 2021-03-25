
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


class Isotherm_pf (Entity):

    _id = 0
    suid = util.getID()
    loaded = False


    # Common / non Property / Private Variables ====================================================================
    owner = 'instance'
    index = int(0)
    parent = util.getID()
    

    # Children initial setup
    

    #  PROPERTIES ================================================================================================
    
    _build_strat = ''
    @property
    def build_strat(self):
        return self._build_strat

    @build_strat.setter
    def build_strat(self, new):
        self.notifyChange('build_strat', self._build_strat, new)
        self._build_strat = new


    _stab_strat = ''
    @property
    def stab_strat(self):
        return self._stab_strat

    @stab_strat.setter
    def stab_strat(self, new):
        self.notifyChange('stab_strat', self._stab_strat, new)
        self._stab_strat = new



    def __init__(self, qlog=None):
        self.loaded = False

        logger = self.configLogger()
        #logger.debug('Isotherm_pf loaded'.format())

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

        instance = Isotherm_pf()
        instance.suid= util.getID()
        if mongolink is not None:
            idx = mongolink.registerEntity({'instance':instance,
                                            'collection':'isotherm_pf',
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

