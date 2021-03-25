

import Util as util
from pydispatch import dispatcher
from BSP import SMStates, SIGNALS, ENTITIES

import logging
logger = logging.getLogger(__name__)

import jsons, json



class Entity(object):

    # ================================================================================================================
    # Notifier to other people
    _dirty = False
    _descriptor = 0

    def notifyChange(self, field, old, new):

        if not self._dirty:
            # dispatcher.send(message=[self, field, old, new], signal=SIGNALS.ENTITYCHANGE, sender=ENTITIES.ENTITY)
            self._dirty = True

    def setUpdated(self):
        self._dirty = False

    def setDirty(self):
        self._dirty = True

    def setDescriptor (self, desc):
        self._descriptor = desc


    #  LOG Services ===================================================================================================
    def configLogger(self, qlog=None):

        logger.setLevel(logging.DEBUG)

        if qlog is None:
            ch = logging.StreamHandler()
        else:
            ch = logging.StreamHandler(qlog)

        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    # Conversion methods ==============================================================================================
    def toJson(self):
        dumped = jsons.dumps(self)
        jobj = json.loads(dumped)
        pp = json.dumps(jobj, indent=4)
        return pp



