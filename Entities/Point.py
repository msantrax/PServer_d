
# Import Section
import re, time
import Util as util
import jsons, json
from typing import List, Set, Tuple, Dict


# Super Class
from Entities.Entity import Entity


# Children Classes
from Entities.Dose import Dose
from Entities.Point_pf import Point_pf


#  Logging Support
import logging
logger = logging.getLogger(__name__)


class Point (Entity):

    _id = 0
    suid = util.getID()
    loaded = False


    # Common / non Property / Private Variables ====================================================================
    owner = 'instance'
    index = int(0)
    parent = util.getID()
    

    # Children initial setup
    doses : List[int] = []
    point_pf : Point_pf
    

    #  PROPERTIES ================================================================================================
    
    _point_num = int(0)
    @property
    def point_num(self):
        return self._point_num

    @point_num.setter
    def point_num(self, new):
        self.notifyChange('point_num', self._point_num, new)
        self._point_num = new


    _point_type = int(0)
    @property
    def point_type(self):
        return self._point_type

    @point_type.setter
    def point_type(self, new):
        self.notifyChange('point_type', self._point_type, new)
        self._point_type = new


    _point_status = 'R'
    @property
    def point_status(self):
        return self._point_status

    @point_status.setter
    def point_status(self, new):
        self.notifyChange('point_status', self._point_status, new)
        self._point_status = new


    _start_ts = int(0)
    @property
    def start_ts(self):
        return self._start_ts

    @start_ts.setter
    def start_ts(self, new):
        self.notifyChange('start_ts', self._start_ts, new)
        self._start_ts = new


    _end_ts = int(0)
    @property
    def end_ts(self):
        return self._end_ts

    @end_ts.setter
    def end_ts(self, new):
        self.notifyChange('end_ts', self._end_ts, new)
        self._end_ts = new


    _point_p0 = float(0.0)
    @property
    def point_p0(self):
        return self._point_p0

    @point_p0.setter
    def point_p0(self, new):
        self.notifyChange('point_p0', self._point_p0, new)
        self._point_p0 = new


    _p_p0 = float(0.0)
    @property
    def p_p0(self):
        return self._p_p0

    @p_p0.setter
    def p_p0(self, new):
        self.notifyChange('p_p0', self._p_p0, new)
        self._p_p0 = new


    _p_end = float(0.0)
    @property
    def p_end(self):
        return self._p_end

    @p_end.setter
    def p_end(self, new):
        self.notifyChange('p_end', self._p_end, new)
        self._p_end = new


    _p_start = float(0.0)
    @property
    def p_start(self):
        return self._p_start

    @p_start.setter
    def p_start(self, new):
        self.notifyChange('p_start', self._p_start, new)
        self._p_start = new


    _point_volume = float(0.0)
    @property
    def point_volume(self):
        return self._point_volume

    @point_volume.setter
    def point_volume(self, new):
        self.notifyChange('point_volume', self._point_volume, new)
        self._point_volume = new


    _void_vol = float(0.0)
    @property
    def void_vol(self):
        return self._void_vol

    @void_vol.setter
    def void_vol(self, new):
        self.notifyChange('void_vol', self._void_vol, new)
        self._void_vol = new


    _dv = float(0.0)
    @property
    def dv(self):
        return self._dv

    @dv.setter
    def dv(self, new):
        self.notifyChange('dv', self._dv, new)
        self._dv = new


    _vtc_sw = float(0.0)
    @property
    def vtc_sw(self):
        return self._vtc_sw

    @vtc_sw.setter
    def vtc_sw(self, new):
        self.notifyChange('vtc_sw', self._vtc_sw, new)
        self._vtc_sw = new


    _vvoid_sw = float(10.0)
    @property
    def vvoid_sw(self):
        return self._vvoid_sw

    @vvoid_sw.setter
    def vvoid_sw(self, new):
        self.notifyChange('vvoid_sw', self._vvoid_sw, new)
        self._vvoid_sw = new


    _tan = int(0)
    @property
    def tan(self):
        return self._tan

    @tan.setter
    def tan(self, new):
        self.notifyChange('tan', self._tan, new)
        self._tan = new


    _ttc = int(0)
    @property
    def ttc(self):
        return self._ttc

    @ttc.setter
    def ttc(self, new):
        self.notifyChange('ttc', self._ttc, new)
        self._ttc = new


    _flag = int(0)
    @property
    def flag(self):
        return self._flag

    @flag.setter
    def flag(self, new):
        self.notifyChange('flag', self._flag, new)
        self._flag = new



    def __init__(self, qlog=None):
        self.loaded = False

        logger = self.configLogger()
        #logger.debug('Point loaded'.format())

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

        instance = Point()
        instance.suid= util.getID()
        if mongolink is not None:
            idx = mongolink.registerEntity({'instance':instance,
                                            'collection':'point',
                                            'id':instance.suid,
                                            'query' : None,
                                            'tstamp' : util.getID(),
                                            'realm' : 'created'
                                            }, instance)
            instance._descriptor = idx
            
        instance.doses = list()
        temp = Dose.getInstance(mongolink, False)
        temp.parent = instance.suid
        instance.doses.append(temp)
 
        instance.point_pf = Point_pf.getInstance(mongolink, False)
        instance.point_pf.parent = instance.suid
 
        return instance

    def toDict(self, embed=False):
        dumped = jsons.dumps(self, embed=embed, caller=self, strip_privates=True)
        jobj = json.loads(dumped)
        return jobj

    def getSerial(self):
        return self.suid


        

    def loaddose(self, mongolink=None, loadchildren=True):

        # Bail out if no mongo connection
        if mongolink is None: return

        for idx, id in enumerate(self.doses):
            if isinstance(id, Dose): continue
            success = mongolink.findEntities(Dose, 'dose', {'suid' : id}, loadchildrens=loadchildren)
            if success :
                register = mongolink.findDescriptor(id)
                if register is not None:
                    child = register['instance']
                    self.doses[idx] = child
                    logger.info('Point loaded Dose {}'.format(child))
                else:
                    logger.info('Entity failed to load Dose {}'.format(id))


    def adddose(self, mongolink=None):

        if isinstance (self.doses[0], int):
            self.loaddoses(mongolink)

        if 'instance' in self.doses[0].owner :
            self.doses[0].owner = ''
            if mongolink : mongolink.setDirty(self.doses[0].suid)
            return self.doses[0]
        else:
            temp = Dose.getInstance(mongolink, False)
            temp.parent = self.suid
            temp.owner = ''
            self.doses.append(temp)
            if mongolink : mongolink.setDirty(self.doses[0].suid)
            return temp


    def removedose(self, idx=None, id=None, mongolink=None):

        if idx is not None:
            temp = self.doses.pop(idx)
            if mongolink is not None:
                mongolink.db.delete_one({'suid': temp.suid})
            return True
        else:
            pass

 
    def loadpoint_pf(self,mongolink=None):

        id = self.point_pf
        success = mongolink.findEntities(Point_pf, 'point_pf', {'suid' : id}, loadchildrens=True)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.point_pf = child
        logger.debug('Point loaded Point_pf {}'.format(child))

 


    def loadChildrens(self, mongolink=None):
        self.loaddose(mongolink)
        self.loadpoint_pf(mongolink)




    #classcode_begin

    #classcode_end

