
&[IMPORTSYS]
# Import Section
import re, time
import Util as util
import jsons, json
from typing import List, Set, Tuple, Dict
$IMPORTS
[IMPORTSYS]&

&[LOGGING]
#  Logging Support
import logging
logger = logging.getLogger(__name__)

[LOGGING]&

&[SUPER]
# Super Class
from $PACKAGEEntity import Entity

[SUPER]&

&[CHILDRENS]
# Children Classes
$CHILDRENS
[CHILDRENS]&


&[CLASSDEF]
class $CLASSNAME (Entity):

    _id = 0
    suid = util.getID()
    loaded = False

[CLASSDEF]&

&[INITVARS]
    # Common / non Property / Private Variables ====================================================================
$INITVARS
[INITVARS]&

&[INITCHILDRENS]
    # Children initial setup
$CHILDINITS
[INITCHILDRENS]&

&[PROPERTIES]
    #  PROPERTIES ================================================================================================
    $PROPERTIES
[PROPERTIES]&

&[PROPERTY]
    _$NAME = $TYPE
    @property
    def $NAME(self):
        return self._$NAME

    @$NAME.setter
    def $NAME(self, new):
        self.notifyChange('$NAME', self._$NAME, new)
        self._$NAME = new

[PROPERTY]&

&[CONSTRUCTOR]
    def __init__(self, qlog=None):
        self.loaded = False

        logger = self.configLogger()
        #logger.debug('$CLASSNAME loaded'.format())
[CONSTRUCTOR]&

&[BASEMETHODS]
    def load (self, input ):
        $LOADBODY
        self.loaded = True

    def parse (self, sparse='', edata=''):
        $PARSEBODY

    def loadDefault(self):
        $DEFAULTBODY

    @classmethod
    def getInstance(cls, mongolink=None, store=True):

        instance = $CLASSNAME()
        instance.suid= util.getID()
        if mongolink is not None:
            idx = mongolink.registerEntity({'instance':instance,
                                            'collection':'$COLLECTION',
                                            'id':instance.suid,
                                            'query' : None,
                                            'tstamp' : util.getID(),
                                            'realm' : 'created'
                                            }, instance)
            instance._descriptor = idx
        $REGISTRIES
        return instance

    def toDict(self, embed=False):
        dumped = jsons.dumps(self, embed=embed, caller=self, strip_privates=True)
        jobj = json.loads(dumped)
        return jobj

    def getSerial(self):
        return self.suid

[BASEMETHODS]&

&[REGISTRY]
        instance$RCHILDVAR = $RCHILDCLASS.getInstance(mongolink, False)
        instance$RCHILDVAR.parent = instance.suid
[REGISTRY]&

&[REGISTRYLIST]
        instance$RCHILDVAR = list()
        temp = $RCHILDCLASS.getInstance(mongolink, False)
        temp.parent = instance.suid
        instance$RCHILDVAR.append(temp)
[REGISTRYLIST]&

&[LISTREGISTRY]
        temp = $RCHILDCLASS.getInstance(mongolink, False)
        temp.parent = instance.suid
        instance.doses.append(temp)
[LISTREGISTRY]&

&[CHILDRENLOAD]
    $LOADMETHODS


$LOADCALLS

[CHILDRENLOAD]&

&[CHILDRENLOADMETHOD]
    def load$CHILDVAR(self,mongolink=None):

        id = self.$CHILDVAR
        success = mongolink.findEntities($CHILDCLASS, '$COLLECTION', {'suid' : id}, loadchildrens=$LOADCHILDREN)
        if success :
            register = mongolink.entity_descriptors[len(mongolink.entity_descriptors)-1]
            child = register['instance']
            self.$CHILDVAR = child
        logger.debug('$CLASSNAME loaded $CHILDCLASS {}'.format(child))

[CHILDRENLOADMETHOD]&

&[CHILDRENLOADLISTMETHOD]

    def load$CHILDVAR(self, mongolink=None, loadchildren=True):

        # Bail out if no mongo connection
        if mongolink is None: return

        for idx, id in enumerate(self.$CHILDVARs):
            if isinstance(id, $CHILDCLASS): continue
            success = mongolink.findEntities($CHILDCLASS, '$CHILDVAR', {'suid' : id}, loadchildrens=loadchildren)
            if success :
                register = mongolink.findDescriptor(id)
                if register is not None:
                    child = register['instance']
                    self.$CHILDVARs[idx] = child
                    logger.info('Point loaded $CHILDCLASS {}'.format(child))
                else:
                    logger.info('Entity failed to load $CHILDCLASS {}'.format(id))


    def add$CHILDVAR(self, mongolink=None):

        if isinstance (self.$CHILDVARs[0], int):
            self.load$CHILDVARs(mongolink)

        if 'instance' in self.$CHILDVARs[0].owner :
            self.$CHILDVARs[0].owner = ''
            if mongolink : mongolink.setDirty(self.$CHILDVARs[0].suid)
            return self.$CHILDVARs[0]
        else:
            temp = $CHILDCLASS.getInstance(mongolink, False)
            temp.parent = self.suid
            temp.owner = ''
            self.$CHILDVARs.append(temp)
            if mongolink : mongolink.setDirty(self.$CHILDVARs[0].suid)
            return temp


    def remove$CHILDVAR(self, idx=None, id=None, mongolink=None):

        if idx is not None:
            temp = self.$CHILDVARs.pop(idx)
            if mongolink is not None:
                mongolink.db.delete_one({'suid': temp.suid})
            return True
        else:
            pass

[CHILDRENLOADLISTMETHOD]&

#====================================================================================================================
&[CLASSMETHODS]
$CMETHODS
[CLASSMETHODS]&
