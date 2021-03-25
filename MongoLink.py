import inspect
import logging
from pymongo import MongoClient, database, collection, cursor
from bson import objectid as oid
import jsons
import json

from threading import Timer

from pydispatch import dispatcher
from BSP import SIGNALS

import Util as util
# from Entities.Point import Point

logger = logging.getLogger(__name__)


class MongoLink(object):

    connected = False
    client: MongoClient
    db: database

    entity_descriptors = list()
    dirty_entities = list()

    col_id = ('isotherm_pf', 'isotherm', 'point_pf', 'point', 'dose_pf', 'dose', 'phase')

    flush_cycle =0

    #  Pointers to Original jsons.dump Serializers (one to each entity class)
    # bp_oserial = jsons.get_serializer(BuildPressure)
    # bp_pf_oserial = jsons.get_serializer(BuildPressure_pf)

    serializers = {}
    deserializers = {}
    entities = {}

    def __init__(self, dbname, qlog=None):

        self.configLogger(qlog)

        atlas = 'mongodb+srv://opus:I7BR0P31Tec9vIZl@antrax-bup.1vkcf.mongodb.net/asvp2'
        local = 'mongodb://localhost:27017'

        try :
            self.client = MongoClient(local)
            self.db = self.client[dbname]
            for col in self.col_id:
                lcol = self.db.get_collection(col)
                name= lcol.name
        except Exception as e :
            logger.debug('Mongolink failed to  {}'.format(e.__repr__()))
            return

        dispatcher.connect(self.entityChanged, signal=SIGNALS.ENTITYCHANGE, sender=dispatcher.Any)
        # collections = self.db.collection_names()

        # Search fo Entities and register them
        m = __import__( 'Entities' )
        for name, obj in inspect.getmembers(m):
            if inspect.ismodule(obj) and getattr(obj, 'Entity'):
                m1 = getattr(obj, name)
                if inspect.isclass(m1) and m1.__name__ is not 'Entity':
                    self.entities[name] = m1
                    self.serializers[m1] = (jsons.get_serializer(m1))
                    self.deserializers[m1] = (jsons.get_deserializer(m1))
                    jsons.set_serializer(MongoLink.entity_serializer, m1)
                    jsons.set_deserializer(MongoLink.entity_deserializer, m1)
        #  Register new serializers to each entity class
        # self.serializers[m1] = (jsons.get_serializer(BuildPressure))
        # self.serializers[BuildPressure_pf] = (jsons.get_serializer(BuildPressure_pf))
        #
        # jsons.set_serializer(MongoLink.entity_serializer, BuildPressure)
        # jsons.set_serializer(MongoLink.entity_serializer, BuildPressure_pf)

        connected = True
        logger.debug('MongoLink started...'.format())




    def clearCollections(self):

        for col in self.col_id:
            self.db.get_collection(col).delete_many({})


    def loadIsotherm(self, id = None, loadch= True):

        clz = self.entities['Isotherm']

        if id is None:
            cp5 = self.findEntities(clz, 'isotherm', {}, loadchildrens=loadch)
        else:
            cp5 = self.findEntities(clz, 'isotherm', {'_id' : id}, loadchildrens=loadch)

        return cp5

    def go(self):

        # cp0 = clz.getInstance(self, store=False)
        # cp0.init_ts = 123456

        self.flush()

        # cp5 = self.findEntities(clz, 'point', {}, loadchildrens=True)
        #cp5 = self.findEntities(clz, 'point', {'_id' : 1613668477993}, loadchildrens=True)

        # t = perpetualTimer(2,self.flush)
        # t.start()

        logger.debug('MongoLink test done'.format())


    def setDirty(self, id):

        if self.connected :
            desc = self.findDescriptor(id)
            if desc is not None:
                if self.findDescriptor(id, dirty=True) is None :
                    self.dirty_entities.append(desc)


    def findDescriptor(self, id, dirty=False):

        if dirty :
            for desc in self.dirty_entities:
                if desc['id'] == id : return desc
            return None
        else:
            for desc in self.entity_descriptors:
                if desc['id'] == id : return desc
            return None


    def findEntities (self, clazz, col, filter, realm = 'generic', loadchildrens = False):

        entities = list()

        cp1dict = self.db[col].find(filter)

        if cp1dict is not None:
            if isinstance(cp1dict, cursor.Cursor ):
                for doc in cp1dict :
                    entities.append(self.loadEntity(doc, clazz, col, filter, realm, loadchildrens))
                # return True if cp1dict.retrieved > 0 else False
            else:
                entities.append(self.loadEntity(cp1dict, clazz, col, filter, realm, loadchildrens))
                # return True
        else:
            logger.debug('Failed to find record {} on {}'.format(filter, col))
            # return False

        return entities


    def loadEntity (self, edict, clazz, col, filter, realm = 'generic', loadchildrens = False):

        record = clazz()

        for k, v in edict.items():
            setattr(record, k, v)

        # if isinstance(record, Point):
        #     record.map(edict)
        # else:
        #     record.__dict__ = edict

        # srecord = json.dumps(edict)
        # record = json.loads(srecord, object_hook=clazz)

        self.entity_descriptors.append({'instance': record,
                                        'collection': col,
                                        'id': record.suid,
                                        'query' : filter,
                                        'tstamp' : util.getID(),
                                        'realm' : realm
                                        })
        desc_index = len(self.entity_descriptors)-1
        record._descriptor = desc_index

        # No every entity has to load childrens so skip if failed to fin
        # attribute
        try :
            if loadchildrens : record.loadChildrens(self)
        except Exception:
            pass

        return record


    def registerEntity (self, descriptor, instance):
        self.entity_descriptors.append(descriptor)
        desc_index = len(self.entity_descriptors)-1

        self.dirty_entities.append(self.entity_descriptors[desc_index])
        return desc_index


    def flush(self):

        self.flush_cycle +=1
        logger.debug('Flushing -> '.format(self.flush_cycle))

        scan = True
        while scan:
            if len(self.dirty_entities) is 0:
                scan = False
            else:
                try:
                    dirty = self.dirty_entities.pop()
                    # iod = oid.ObjectId()
                    if dirty['instance']._id == 0 : dirty['instance']._id = oid.ObjectId()
                    bp1=dirty['instance'].toDict(embed=True)
                    idx = {'suid': dirty['instance'].suid}
                    result = self.db[dirty['collection']].replace_one(idx, bp1, upsert=True)
                    logger.debug('Entity : {} has been flushed with result {}'.format(dirty['id'], result.upserted_id))
                    dirty['instance'].setUpdated()
                except Exception as e:
                    logger.debug('Failed to flush due {}'.format(e.__repr__()))



    # Serializers ====================================================================================

    @classmethod
    def entity_serializer(mongocls, obj , embed=True, caller=None,  **kwargs) :
        if isinstance(caller,  obj.__class__):
            func = mongocls.serializers[obj.__class__]
            ret = func(obj, strip_privates=True)
            # ret = func(obj)
            return ret
        else:
            return obj.getSerial()

    @classmethod
    def entity_deserializer(mongocls, obj, cls, embed=True, dumped=None,  **kwargs) :
        try:
            obj['doses'] = 1
            return json.loads(jsons.dumps(obj))
        except Exception as e :
            logger.debug('Failed to deserialize due {}'.format(e.__repr__()))


    def configLogger(self, qlog=None):

        logger.setLevel(logging.DEBUG)

        if qlog is None:
            ch = logging.StreamHandler()
        else:
            ch = logging.StreamHandler(qlog)

        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


    def entityChanged(self, message):

        idx = message[0]._descriptor
        self.dirty_entities.append(self.entity_descriptors[idx])
        logger.debug('Entity {} changed from {} to {}'.format(message[0], message[1], message[2]))


class perpetualTimer():

    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = Timer(self.t,self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t,self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()





# ==================================================================================================================


# def createNewDB(self, dbname):
#
#     lclient = MongoClient('mongodb://localhost:27017')
#     ldb = self.lclient[dbname]
#
#     try :
#         for col in self.col_id:
#             lcol = ldb.get_collection(col)
#             name= lcol.name
#
#     except Exception as e :
#         logger.debug('Mongolink failed to  {}'.format(e.__repr__()))
#         return
#     logger.debug('Database {} was created on Mongolink'.format(dbname))
