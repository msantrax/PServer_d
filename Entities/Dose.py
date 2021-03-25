
# Import Section
import re, time
import Util as util
import jsons, json
from typing import List, Set, Tuple, Dict


# Super Class
from Entities.Entity import Entity


# Children Classes
from Entities.Dose_pf import Dose_pf
from Entities.Phase import Phase


#  Logging Support
import logging
logger = logging.getLogger(__name__)


class Dose (Entity):

    _id = 0
    suid = util.getID()
    loaded = False


    # Common / non Property / Private Variables ====================================================================
    owner = 'instance'
    index = int(0)
    parent = util.getID()
    

    # Children initial setup
    dose_pf : Dose_pf
    buildp_phase : Phase
    stabinit_phase : Phase
    stabend_phase : Phase
    

    #  PROPERTIES ================================================================================================
    
    _dose_type = int(0)
    @property
    def dose_type(self):
        return self._dose_type

    @dose_type.setter
    def dose_type(self, new):
        self.notifyChange('dose_type', self._dose_type, new)
        self._dose_type = new


    _ach_dp = float(1.778)
    @property
    def ach_dp(self):
        return self._ach_dp

    @ach_dp.setter
    def ach_dp(self, new):
        self.notifyChange('ach_dp', self._ach_dp, new)
        self._ach_dp = new


    _ach_tol = float(2.795)
    @property
    def ach_tol(self):
        return self._ach_tol

    @ach_tol.setter
    def ach_tol(self, new):
        self.notifyChange('ach_tol', self._ach_tol, new)
        self._ach_tol = new


    _achieved = float(63.627)
    @property
    def achieved(self):
        return self._achieved

    @achieved.setter
    def achieved(self, new):
        self.notifyChange('achieved', self._achieved, new)
        self._achieved = new


    _target = float(61.664)
    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, new):
        self.notifyChange('target', self._target, new)
        self._target = new


    _initialp = float(130.987)
    @property
    def initialp(self):
        return self._initialp

    @initialp.setter
    def initialp(self, new):
        self.notifyChange('initialp', self._initialp, new)
        self._initialp = new


    _ts_init = int(util.getID())
    @property
    def ts_init(self):
        return self._ts_init

    @ts_init.setter
    def ts_init(self, new):
        self.notifyChange('ts_init', self._ts_init, new)
        self._ts_init = new


    _ts_ach = int(util.getID())
    @property
    def ts_ach(self):
        return self._ts_ach

    @ts_ach.setter
    def ts_ach(self, new):
        self.notifyChange('ts_ach', self._ts_ach, new)
        self._ts_ach = new


    _ts_stabinit = int(util.getID())
    @property
    def ts_stabinit(self):
        return self._ts_stabinit

    @ts_stabinit.setter
    def ts_stabinit(self, new):
        self.notifyChange('ts_stabinit', self._ts_stabinit, new)
        self._ts_stabinit = new


    _ts_stabend = int(util.getID())
    @property
    def ts_stabend(self):
        return self._ts_stabend

    @ts_stabend.setter
    def ts_stabend(self, new):
        self.notifyChange('ts_stabend', self._ts_stabend, new)
        self._ts_stabend = new


    _redose = False
    @property
    def redose(self):
        return self._redose

    @redose.setter
    def redose(self, new):
        self.notifyChange('redose', self._redose, new)
        self._redose = new


    _redose_p2 = float(48.997)
    @property
    def redose_p2(self):
        return self._redose_p2

    @redose_p2.setter
    def redose_p2(self, new):
        self.notifyChange('redose_p2', self._redose_p2, new)
        self._redose_p2 = new


    _redose_time = float(33.0)
    @property
    def redose_time(self):
        return self._redose_time

    @redose_time.setter
    def redose_time(self, new):
        self.notifyChange('redose_time', self._redose_time, new)
        self._redose_time = new


    _equilibrium = False
    @property
    def equilibrium(self):
        return self._equilibrium

    @equilibrium.setter
    def equilibrium(self, new):
        self.notifyChange('equilibrium', self._equilibrium, new)
        self._equilibrium = new


    _equilibrium_dp = float(0)
    @property
    def equilibrium_dp(self):
        return self._equilibrium_dp

    @equilibrium_dp.setter
    def equilibrium_dp(self, new):
        self.notifyChange('equilibrium_dp', self._equilibrium_dp, new)
        self._equilibrium_dp = new


    _equilibrium_count = float(0.0)
    @property
    def equilibrium_count(self):
        return self._equilibrium_count

    @equilibrium_count.setter
    def equilibrium_count(self, new):
        self.notifyChange('equilibrium_count', self._equilibrium_count, new)
        self._equilibrium_count = new



    def __init__(self, qlog=None):
        self.loaded = False

        logger = self.configLogger()
        #logger.debug('Dose loaded'.format())

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

        instance = Dose()
        instance.suid= util.getID()
        if mongolink is not None:
            idx = mongolink.registerEntity({'instance':instance,
                                            'collection':'dose',
                                            'id':instance.suid,
                                            'query' : None,
                                            'tstamp' : util.getID(),
                                            'realm' : 'created'
                                            }, instance)
            instance._descriptor = idx
            
        instance.dose_pf = Dose_pf.getInstance(mongolink, False)
        instance.dose_pf.parent = instance.suid
 
        instance.buildp_phase = Phase.getInstance(mongolink, False)
        instance.buildp_phase.parent = instance.suid
 
        instance.stabinit_phase = Phase.getInstance(mongolink, False)
        instance.stabinit_phase.parent = instance.suid
 
        instance.stabend_phase = Phase.getInstance(mongolink, False)
        instance.stabend_phase.parent = instance.suid
 
        return instance

    def toDict(self, embed=False):
        dumped = jsons.dumps(self, embed=embed, caller=self, strip_privates=True)
        jobj = json.loads(dumped)
        return jobj

    def getSerial(self):
        return self.suid


        
    def loaddose_pf(self,mongolink=None):

        id = self.dose_pf
        success = mongolink.findEntities(Dose_pf, 'dose_pf', {'suid' : id}, loadchildrens=True)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.dose_pf = child
        logger.debug('Dose loaded Dose_pf {}'.format(child))

 
    def loadbuildp_phase(self,mongolink=None):

        id = self.buildp_phase
        success = mongolink.findEntities(Phase, 'phase', {'suid' : id}, loadchildrens=True)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.buildp_phase = child
        logger.debug('Dose loaded Phase {}'.format(child))

 
    def loadstabinit_phase(self,mongolink=None):

        id = self.stabinit_phase
        success = mongolink.findEntities(Phase, 'phase', {'suid' : id}, loadchildrens=True)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.stabinit_phase = child
        logger.debug('Dose loaded Phase {}'.format(child))

 
    def loadstabend_phase(self,mongolink=None):

        id = self.stabend_phase
        success = mongolink.findEntities(Phase, 'phase', {'suid' : id}, loadchildrens=True)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.stabend_phase = child
        logger.debug('Dose loaded Phase {}'.format(child))

 


    def loadChildrens(self, mongolink=None):
        self.loaddose_pf(mongolink)
        self.loadbuildp_phase(mongolink)
        self.loadstabinit_phase(mongolink)
        self.loadstabend_phase(mongolink)




    #classcode_begin

    #classcode_end

