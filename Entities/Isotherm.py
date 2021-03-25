
# Import Section
import re, time
import Util as util
import jsons, json
from typing import List, Set, Tuple, Dict


# Super Class
from Entities.Entity import Entity


# Children Classes
from Entities.Point import Point
from Entities.Isotherm_pf import Isotherm_pf


#  Logging Support
import logging
logger = logging.getLogger(__name__)


class Isotherm (Entity):

    _id = 0
    suid = util.getID()
    loaded = False


    # Common / non Property / Private Variables ====================================================================
    owner = 'instance'
    index = int(0)
    parent = util.getID()
    

    # Children initial setup
    points : List[int] = []
    isotherm_pf : Isotherm_pf
    

    #  PROPERTIES ================================================================================================
    
    _iso_num = int(0)
    @property
    def iso_num(self):
        return self._iso_num

    @iso_num.setter
    def iso_num(self, new):
        self.notifyChange('iso_num', self._iso_num, new)
        self._iso_num = new


    _iso_status = ''
    @property
    def iso_status(self):
        return self._iso_status

    @iso_status.setter
    def iso_status(self, new):
        self.notifyChange('iso_status', self._iso_status, new)
        self._iso_status = new



    def __init__(self, qlog=None):
        self.loaded = False

        logger = self.configLogger()
        #logger.debug('Isotherm loaded'.format())

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

        instance = Isotherm()
        instance.suid= util.getID()
        if mongolink is not None:
            idx = mongolink.registerEntity({'instance':instance,
                                            'collection':'isotherm',
                                            'id':instance.suid,
                                            'query' : None,
                                            'tstamp' : util.getID(),
                                            'realm' : 'created'
                                            }, instance)
            instance._descriptor = idx
            
        instance.points = list()
        temp = Point.getInstance(mongolink, False)
        temp.parent = instance.suid
        instance.points.append(temp)
 
        instance.isotherm_pf = Isotherm_pf.getInstance(mongolink, False)
        instance.isotherm_pf.parent = instance.suid
 
        return instance

    def toDict(self, embed=False):
        dumped = jsons.dumps(self, embed=embed, caller=self, strip_privates=True)
        jobj = json.loads(dumped)
        return jobj

    def getSerial(self):
        return self.suid


        

    def loadpoint(self, mongolink=None, loadchildren=True):

        # Bail out if no mongo connection
        if mongolink is None: return

        for idx, id in enumerate(self.points):
            if isinstance(id, Point): continue
            success = mongolink.findEntities(Point, 'point', {'suid' : id}, loadchildrens=loadchildren)
            if success :
                register = mongolink.findDescriptor(id)
                if register is not None:
                    child = register['instance']
                    self.points[idx] = child
                    logger.info('Point loaded Point {}'.format(child))
                else:
                    logger.info('Entity failed to load Point {}'.format(id))


    def addpoint(self, mongolink=None):

        if isinstance (self.points[0], int):
            self.loadpoints(mongolink)

        if 'instance' in self.points[0].owner :
            self.points[0].owner = ''
            if mongolink : mongolink.setDirty(self.points[0].suid)
            return self.points[0]
        else:
            temp = Point.getInstance(mongolink, False)
            temp.parent = self.suid
            temp.owner = ''
            self.points.append(temp)
            if mongolink : mongolink.setDirty(self.points[0].suid)
            return temp


    def removepoint(self, idx=None, id=None, mongolink=None):

        if idx is not None:
            temp = self.points.pop(idx)
            if mongolink is not None:
                mongolink.db.delete_one({'suid': temp.suid})
            return True
        else:
            pass

 
    def loadisotherm_pf(self,mongolink=None):

        id = self.isotherm_pf
        success = mongolink.findEntities(Isotherm_pf, 'isotherm_pf', {'suid' : id}, loadchildrens=True)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.isotherm_pf = child
        logger.debug('Isotherm loaded Isotherm_pf {}'.format(child))

 


    def loadChildrens(self, mongolink=None):
        self.loadpoint(mongolink)
        self.loadisotherm_pf(mongolink)




    #classcode_begin

    #classcode_end

