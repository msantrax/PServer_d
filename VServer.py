import click
import logging
import sys
import inspect
import locale
import re, time, os, shutil


from MongoLink import MongoLink

import Util as util

from PBeanBuilder import PBeanBuilder
from JBeanBuilder import JBeanBuilder
from QCRImporter import QCRImporter
from LogScanner import LogScanner, ITPoint, ITDose

from Entities import Isotherm



logger = logging.getLogger(__name__)

@click.command()
@click.option('--siteurl', default="http://anfitria.club", help='Site to scrap')
@click.option('--sfile', default="scrap2.html", help='Storage File')



def start (sfile, siteurl):

    locale.setlocale(locale.LC_ALL, '')

    configLogger()
    util.configLogger()

    mongolink = MongoLink('asvp2', None)

    # qcrimporter = QCRImporter(None)
    # logscanner = LogScanner(None)

    # pbean = JBeanBuilder()
    # pbean.loadTemplate('Dose')

    # exerciseIso(mongolink)

    # isotherms = mongolink.loadIsotherm(loadch=True)
    # iso1:Isotherm = isotherms[0]
    # iso1.loadpoint(mongolink, loadchildren=True)

    # buildJAll()
    # buildAll()
    # buildIsotherm(mongolink, clear= False, prange = None)

    logger.info('Done !')


def testNewDB(mongolink, dbname):

    mongolink.createNewDB(dbname)
    buildIsotherm(mongolink, True, 5)

    # isotherms = mongolink.loadIsotherm(loadch=False)
    # iso1:Isotherm = isotherms[0]
    # iso1.loadpoint(mongolink, loadchildren=False)




def buildIsotherm(mongolink = None, clear = True, prange = None):

    if mongolink is not None and clear:
        mongolink.clearCollections()

    logscanner = LogScanner(None)
    isotherm = mongolink.entities['Isotherm'].getInstance(mongolink)
    isotherm.iso_status = 'test'
    isotherm.iso_num = 10


    if prange is None : prange = len(logscanner.spoints_list)
    for idx in range(prange):
        point = isotherm.addpoint(mongolink)
        pdata:ITPoint = logscanner.spoints_list[idx]

        point.point_p0 = pdata.P0
        point.dv = pdata.dV
        point.end_ts = pdata.ts_end
        point.p_end = pdata.pressure_end
        point.p_p0 = pdata.pressure_p0
        point.p_start = pdata.pressure_start
        point.point_num = pdata.pointnum
        point.start_ts = pdata.ts_start
        point.tan = pdata.tan
        point.ttc = pdata.ttc
        point.void_vol = pdata.void_volume
        point.point_volume = pdata.volume_g
        point.vtc_sw = pdata.vtc_sw
        point.vvoid_sw = pdata.vvoid_sw
        point.point_type = 0 if pdata.adspoint else 1

        for t in pdata.doses_list:
            doses_status = 'G'
            ds:ITDose = t
            dose = point.adddose(mongolink)
            dose.ach_dp = ds.ach_dP
            dose.ach_tol = ds.ach_tol
            dose.achieved = ds.achieved
            dose.equilibrium = ds.equilibrium
            dose.equilibrium_count = ds.equ_count
            dose.equilibrium_dp = ds.equ_dP
            dose.initialp = ds.initialp
            dose.redose = ds.redose
            dose.redose_p2 = ds.redose_p2
            dose.redose_time = ds.redose_time
            dose.target = ds.target_pressure
            dose.ts_ach = ds.ts_achieved
            dose.ts_init = ds.ts_init
            dose.ts_stabinit = ds.ts_stabinit
            dose.ts_stabend = ds.ts_stabend
            dose.ts_init = ds.ts_init
            dose.ts_ach = ds.ts_achieved
            dose.dose_type = 0
            if dose.equilibrium :
                dose.dose_type = 1
                doses_status = 'E'
            if dose.redose :
                dose.dose_type = 2
                doses_status = 'R'

        point.point_status = doses_status

    mongolink.go()
    return isotherm


def buildAll():

    entities_path = '/Bascon/ASVP/PSERVER/Sandbox/PServer_d/Entities/'
    bentities = ('Dose', 'Dose_pf', 'Isotherm', 'Isotherm_pf', 'Phase', 'Point', 'Point_pf')

    for bent in bentities:
        fpath = entities_path + bent + '.py'
        if os.path.exists(fpath):
            os.remove(fpath)
        pbean = PBeanBuilder()
        pbean.loadTemplate(bent)

def buildJAll():

    entities_path = '/Bascon/ASVP/ASVP_ANA/Sandbox/MiddleStripB/src/Entities/'
    bentities = ['Dose', 'Dose_pf', 'Isotherm', 'Isotherm_pf', 'Phase', 'Point', 'Point_pf']

    # bentities = ['Isotherm']

    for bent in bentities:
        fpath = entities_path + bent + '.java'
        if os.path.exists(fpath):
            os.remove(fpath)
        jbean = JBeanBuilder()
        jbean.loadTemplate(bent)



def oldStuff():

    # cterm = CTerm()
    # term_inq = cterm.get_inqueue()
    # qlog = LogQueue(term_inq)
    # configLogger(qlog)
    #
    # isthscanner = IsthScanner(qlog)
    # # bascon = Bascon(qlog)
    #
    # sm = RunSM(qlog, isthscanner)
    #
    # cterm.go()
    # sm.go()
    #
    # logger.info('Logging from root')
    # dispatcher.send(message='message from root', signal=SIGNALS.TERM_WRITELINE, sender=ENTITIES.ROOT)
    # dispatcher.connect(runsm_dispatcher_quit, signal=SIGNALS.QUIT, sender=dispatcher.Any)
    #
    # isthscanner.go()
    pass

def exerciseIso(mongolink = None, m= None):

    # point = Point.Point.getInstance(mongolink=mongolink)
    # for i in range(5):
    #     dose = point.addDose(mongolink=mongolink)
    #     dose.index = i

    isotherm = mongolink.entities['Isotherm'].getInstance(mongolink)
    point = isotherm.addpoint(mongolink)
    point.index = 3
    for _ in range(3):
        point.adddose(mongolink)
    point = isotherm.addpoint(mongolink)
    point.index = 4
    for _ in range(5):
        point.adddose(mongolink)

    if mongolink is not None:
        mongolink.clearCollections()
        mongolink.go()


def runsm_dispatcher_quit():
    sys.exit()


def configLogger(qlog=None):
    logger.setLevel(logging.DEBUG)

    if qlog is None:
        ch = logging.StreamHandler()
    else:
        ch = logging.StreamHandler(qlog)

    formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class LogQueue:

    def __init__(self, q):
        self.q = q

    def write(self, t):
        t = t.strip('\n')
        # print(t)
        self.q.put(t)

    def flush(self):
        pass


if __name__ == '__main__':
    start()




#=====================================================================================================


# from twisted.internet import stdio
# from twisted.protocols import basic
# from twisted.internet import reactor
# from os import linesep

    # stdio.StandardIO(Echo())
    # reactor.run()

# class Echo(basic.LineReceiver):
#     delimiter = linesep.encode("ascii")
#
#     def __init__(self):
#         # self.setRawMode()
#         pass
#
#     def connectionMade(self):
#         self.transport.write(b'Virna> ')
#
#
#     def lineReceived(self, line):
#         self.sendLine(b'Line: ' + line)
#         self.transport.write(b'>>> ')
#
#
#     def rawDataReceived(self, data):
#         self.sendLine(b'Raw: ' + data)
#         self.transport.write(b'>>> ')
#
#     def DataReceived(self, data):
#         self.sendLine(b'Data: ' + data)




# ep1 = util.SDate2Epoch (r'May 28 21:23:23 2013')
    # ep1 = util.SDate2JavaMillis('December 30 10:27:58 2020')
# logger.debug ('SDate {} converted to : {} '.format(datetime.strptime('December 30 10:27:58 2020',
    #                                                                      '%B %d %H:%M:%S %Y'), ep1))



    # logger.debug('Timestamps are  {} -- {} '.format( util.Epoch2SDate(ep1),
    #                                                  util.Epoch2SDate(ep2)))

    # # ct stores current time
    # ct = datetime.now()
    # print("current time:-", ct)
    #
    # # ts store timestamp of current time
    # ts = ct.timestamp()*1000
    # print("timestamp:-", ts)


# ep2 = util.LocatedDate2JavaMillis('BuildPressure(23.802 780.000 751.697)mmHg [VOL Down] December 30 10:27:58 2020')
# logger.debug('TailDate converted to : {} '.format(ep2))

# public ArrayList<Long> getPoints() {
#     ArrayList<Long>t = new ArrayList<>();
# t.add(12L);
# return t;
# }
# public void setPoints(ArrayList<Object> points) {this.points = points;}


# @Override
# public void flushRecord(){
#
#     MongoCollection<$CLASSNAME> coll = mongolink.getDatabase().getCollection("$COLLECTION", $CLASSNAME.class);
# EntityDescriptor ed = this._descriptor;
# if (ed.getStatus() == EntityDescriptor.Status.CREATE){
# coll.insertOne(this);
# }
# else if (ed.getStatus() == EntityDescriptor.Status.UPDATE){
# coll.replaceOne(eq("suid", this.suid), this);
# }
# }



    #
    # _id = document.get("_id", ObjectId.class);
    # suid = document.get("suid", Long.class);
    # loaded = document.get("loaded", Boolean.class);
    # points = document.get("points", ArrayList.class);
    # isotherm_pf = document.get("isotherm_pf", Long.class);
    # owner = document.get("owner", String.class);
    # index = document.get("index", Integer.class);
    # parent = document.get("parent", Long.class);
    # iso_num = document.get("iso_num", Integer.class);
    # iso_status = document.get("iso_status", String.class);
