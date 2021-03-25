
import logging, re

from pydispatch import dispatcher
from BSP import SIGNALS, ENTITIES

import Util as util

logger = logging.getLogger(__name__)


class LogScanner:

    filepath=''
    seed_datalist=list()
    sdata = ''

    spoints_list = list();

    regexes = {
        "gpoint_selector": re.compile(r"(Saved)(.*?)(N320601.dat)",re.MULTILINE | re.DOTALL | re.VERBOSE),
        "fpoint_selector": re.compile(r""),
        "totalpnts": re.compile(r"(.{24})TotalPntsReq=.*?DoseSta=(.{3}).*?atPoint=(.{2}).*?DoP0=(.{2}).*?P0SoFar=(.{2})"),
        "void_volume": re.compile(r"(.{24})VoidVolumeCell\[.\] =(.{8})", re.MULTILINE | re.DOTALL | re.VERBOSE ),
        "dose_selector": re.compile(r"(.{24})Build(.*?)(.{24})!A(.*?Up\])", re.MULTILINE | re.DOTALL | re.VERBOSE ),
        "build_pressure": re.compile(r"Pressure(.{7}).*?xover(.{7}).*?InitialP:(.{7})", re.MULTILINE | re.DOTALL | re.VERBOSE ),
        "achieved": re.compile(r"(.{24})Achieved:\sP(.{7}).*?tol(.{7})dP(.{7})Vact=(.{4})Gast=(.{3})loop=(.{2})", re.MULTILINE | re.DOTALL | re.VERBOSE ),
        "stabinit": re.compile(r"(.{24})\s\s\[STA t UP\]", re.MULTILINE | re.DOTALL | re.VERBOSE ),
        "redose": re.compile(r"Redose\sin(.{3}).*?P2=(.{7})", re.MULTILINE | re.DOTALL | re.VERBOSE ),
        "equilibrium": re.compile(r"EQUILIBRIUM!\sCount\s=(.{4}).*?P\s=(.{7}).*?", re.MULTILINE | re.DOTALL | re.VERBOSE )
        # "params": re.compile(r"EQUILIBRIUM!\sCount\s=(.{4}).*?P\s=(.{7}).*?", re.MULTILINE | re.DOTALL | re.VERBOSE )
    }

    last_pressure = float()

    def __init__(self, qlog, filepath = '/Bascon/ASVP/Quantawin/Data_190121/Seg3/NWLOG_A.log'):

        self.configLogger(qlog)
        self.filepath = filepath
        self.loadlog([filepath])
        self.scan()

        logger.debug('Finished load {} points'.format(len(self.spoints_list)))
        sts = self.listStatus()
        logger.debug(sts)

        # try:
        #     outpath = '/Bascon/ASVP/Quantawin/Data_190121/Seg3/status.log'
        #     with open(outpath, 'wt') as fhandle:
        #         fhandle.write(sts)
        #         fhandle.close()
        # except Exception as e :
        #     logger.debug('LogScanner failed to save status on {} due {}'.format(outpath, e.__repr__()))


    def loadlog(self, payload):

        if payload.__len__() == 0:
            logger.warning("setSource : Pointing to nothing ?")
        else:
            fpath = payload[0]
            logger.debug('LogScanner Source pointing to : {}'.format(fpath))
            try:
                with open(fpath, 'rt') as fhandle:
                    self.sdata = fhandle.read()
                    self.filepath = fpath
                    self.seed_datalist = self.sdata.split('\n')
                    logger.debug('LogScanner has loaded {} lines'.format(len(self.seed_datalist)))
                    fhandle.close()
            except Exception as e :
                logger.debug('LogScanner failed to load file {} due {}'.format(fpath, e.__repr__()))


    def scan(self):

        try:

            mpat = re.compile(r'Preparing(.*?)Saving', re.MULTILINE | re.DOTALL | re.VERBOSE )
            m0 = re.findall(mpat, self.sdata)
            if m0 is not None and len(m0) > 0:
                mpat1 = re.compile(r'\$A;1;(.*?)$', re.MULTILINE | re.DOTALL | re.VERBOSE )
                m1 = re.findall(mpat1, m0[0])
                if m1 is not None and len(m1)>0 :
                    itpoint = ITPoint(m0[0], m1[0])
                    itpoint.pressure_start = 0.0
                    self.last_pressure = itpoint.pressure_end
                    #itpoint.loadParams()

                self.last_pressure = itpoint.pressure_end
                self.spoints_list.append(itpoint)

            m = re.findall(self.regexes["gpoint_selector"], self.sdata)
            if m is not None and len(m) > 0:
                for pointdata in m :
                    spoint = str(pointdata[1])
                    if (spoint.startswith(" data")):
                        itpoint = ITPoint(spoint)
                        itpoint.pressure_start = self.last_pressure
                        self.last_pressure = itpoint.pressure_end
                        self.spoints_list.append(itpoint)

                        if (itpoint.pressure_end < itpoint.pressure_start):
                            itpoint.adspoint = False

                        # return
                        # logger.debug('Loaded point {}'.format(itpoint.pointnum))

        except Exception as e :
            logger.debug('Logscanner failed interpret due {}'.format(e.__repr__()))


    def listStatus(self):

        pt0:ITPoint = self.spoints_list[0]
        ts_stsstart = pt0.ts_start
        lastp=0.0

        sb = util.StringBuilder('')


        for ptx in self.spoints_list:
            ptxa:ITPoint = ptx

            if ptxa.pointnum > 30 : break
            ldose = ptxa.doses_list[len(ptxa.doses_list)-1]
            if ldose.redose :
                dsts = "R"
            elif ldose.equilibrium:
                dsts = "E"
            else :
                dsts = "G"

            sdoses = self.getDosesTable(ptxa, lastp)

            l1 = '{:<3d}{:2}{:8d}{:8d}{:6d} | {:9.4f} {:9.4f} {:8.4f} ({:6.4f}) - {:>2}{}({:8.4f}/{:8.4f}) {}\n'.format(
                                                ptxa.pointnum,
                                                ptxa.adspoint,
                                                int((ptxa.ts_start-ts_stsstart)/1000),
                                                int((ptxa.ts_end-ts_stsstart)/1000),
                                                int((ptxa.ts_end - ptxa.ts_start)/1000),
                                                ptxa.pressure_start,
                                                ptxa.pressure_end,
                                                ptxa.pressure_end - ptxa.pressure_start,
                                                ptxa.pressure_p0,
                                                len(ptxa.doses_list),
                                                dsts,
                                                sdoses[0],
                                                ptxa.cor,
                                                sdoses[1]
                                                     )
            sb+= l1
            lastp = ptxa.pressure_end

        return '\n'+ str(sb)



    def getDosesTable(self, itpoint, lastp):

        sb = util.StringBuilder('[')

        volume = 0.0
        firstp = itpoint.doses_list[0].achieved
        sb+= '({:7.3f}/{:7.3f})'.format(lastp, firstp - lastp)

        for dose in itpoint.doses_list:
            dsts = ""
            if dose.redose :
                dsts = "R:({:02.0f}){:7.3f}".format(dose.redose_time, dose.redose_p2)
                volume += dose.achieved - dose.redose_p2
            elif dose.equilibrium:
                dsts = "E:{:7.3f}".format(itpoint.pressure_end)
                volume += dose.achieved - itpoint.pressure_end
            else :
                dsts = "G:{:7.3f}".format(itpoint.pressure_end)
                volume += dose.achieved - itpoint.pressure_end

            l1 = '|{:7.3f}->{}'.format(
                    dose.achieved,
                    dsts
            )
            sb+=l1

        sb+=']'
        return (volume, str(sb))


    def configLogger(self, qlog=None):

        logger.setLevel(logging.DEBUG)

        if qlog is None:
            ch = logging.StreamHandler()
        else:
            ch = logging.StreamHandler(qlog)

        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


class ITPoint:

    sdata = str()
    doses_list = list()

    adspoint = True

    void_volume = float()

    volume_g = float()
    volume_r = float()

    pressure_start = float()
    pressure_end = float()
    pressure_p0 = float()
    pressure_r = float()

    ts_start = int(0)
    ts_end = int(0)


    #Params
    pointnum = int()
    P_P0 = float()
    tan = int()
    ttc = int()
    cor = float()
    vtc_sw = float()
    dV = float()
    vvoid_sw = float()
    P0 = float()


    def __init__(self, sdata, sparams = None):
        self.sdata = sdata
        self.doses_list = list()

        self.loadParams(sparams)
        self.loadDoses()

        mpat = re.compile(r"Pressure:(.{7}).*?Volume:(.{8})", re.MULTILINE | re.DOTALL | re.VERBOSE )
        m = re.findall(mpat, self.sdata)
        if m is not None and len(m) > 0:
            self.volume_g = self.cor
            self.pressure_p0 = float(m[0][0])
            self.pressure_r = self.P0 * self.pressure_p0
            self.pressure_end = self.pressure_r




        # logger.debug('Found {} doses'.format(len(self.doses_list)))


    def loadDoses (self):

        #Trap1
        # if self.pointnum == 29:
        #     logger.debug('Trapped on point {}'.format(self.pointnum))

        try:
            mpat = re.compile(r"(.{24})Build(.*?)(STA\st\sUp\](.{65}))", re.MULTILINE | re.DOTALL | re.VERBOSE )
            m = re.findall(mpat, self.sdata)
            if m is not None and len(m) > 0:
                for dose in m :
                    sdose = str(dose[1]+dose[2])
                    dosebean = ITDose(sdose, util.SDate2JavaMillis(dose[0], '%b %d %H:%M:%S %Y'))
                    if (self.ts_start == 0) : self.ts_start = dosebean.ts_init
                    self.doses_list.append(dosebean)
                    dosebean.finishDose(util.SDate2JavaMillis(dose[3][:22],'%b %d %H:%M:%S %Y'), dose[3][28:])

                self.ts_end = dosebean.ts_stabend

                # logger.debug('Found {} doses'.format(len(self.doses_list)))

        except Exception as e :
            logger.debug('ITPoint failed load dose due {}'.format(e.__repr__()))


    def updateParams (self, plist):

        params_list = plist.split(";")
        self.pointnum = int(params_list[0])
        self.P_P0 = float(params_list[1])
        self.tan = int(params_list[2])
        self.ttc = int(params_list[3])
        self.cor = float(params_list[4])

        self.vtc_sw = float(params_list[5])
        self.volume_g = float(params_list[5])

        self.dV = float(params_list[6])
        self.vvoid_sw = float(params_list[7])
        self.P0 = float(params_list[8])

        # logger.debug('Found {} params'.format(len(params_list)))


    def loadParams(self, m=None):

        try:
            if m is None:
                mpat = re.compile(r"(.{24})\$A(.*)Pressure:(.{7})", re.MULTILINE | re.DOTALL | re.VERBOSE )
                m = re.findall(mpat, self.sdata)
                if m is not None and len(m) > 0:
                    params1 = str(m[0][1])
                    params_end = params1.find('\n')
                    self.updateParams(params1[1:params_end])
                else:
                    logger.debug('LoadParams failed to locate stream')
                    return
            else:
                self.updateParams('1;'+ m)

        except Exception as e :
            logger.debug('ITPoint failed to load params due {}'.format(e.__repr__()))



class ITDose:

    ts_init = int()
    target_pressure = float()
    xover = float()
    initialp = float()

    ts_achieved = int()
    achieved = float()
    ach_tol = float()
    ach_dP = float()
    vact = float()
    gast = float()
    loop = float()

    ts_stabinit = int()
    redose = False
    ts_stabend = int()

    redose_time = float()
    redose_p2 = float()

    equilibrium = False
    equ_count = float()
    equ_dP = float()



    sdata = str()
    def __init__(self, sdata, ts_init):
        self.sdata = sdata
        self.ts_init = ts_init
        self.scanDose()


    def finishDose(self, end_ts:int, redose:str):
        self.ts_stabend = end_ts

        try:
            mpat = re.compile(r"Redose\sin(.{1,3}).*P2=(.{7})", re.MULTILINE | re.DOTALL | re.VERBOSE )
            m = re.findall(mpat, redose)
            if m is not None and len(m) > 0:
                self.redose = True
                self.redose_time = float(m[0][0].replace("s", ""))
                self.redose_p2 = float(m[0][1])
                return;

            #"equilibrium": re.compile(r"EQUILIBRIUM!\sCount\s=(.{4}).*?P\s=(.{7})", re.MULTILINE | re.DOTALL | re.VERBOSE )
            # mpat = re.compile(r"EQUILIBRIUM!\sCount\s=(.{4}).*?P\s=(.{7}).*?", re.MULTILINE | re.DOTALL | re.VERBOSE )
            m1 = re.findall(LogScanner.regexes["equilibrium"], redose)
            if len(m1) > 0:
                self.equilibrium = True
                self.equ_count = float(m1[0][0])
                self.equ_dP = float(m1[0][1])


        except Exception as e :
            logger.debug('FinishDose failed define dose type due {}'.format(e.__repr__()))



    def scanDose (self):

        try:
            m = re.findall(LogScanner.regexes["build_pressure"], self.sdata)
            if m is not None:
                self.target_pressure = float(m[0][0])
                self.xover = float(m[0][1])
                self.initialp = float(m[0][2])


            mpat = re.compile(r"(.{24})Achieved:\sP(.{7}).*?tol(.{7})dP(.{7})Vact=(.{2,4})Gast=(.{3})loop=(.{2})", re.MULTILINE | re.DOTALL | re.VERBOSE )
            m1 = re.findall(mpat, self.sdata)
            if m1 is not None:
                self.ts_achieved = util.SDate2JavaMillis(m1[0][0], '%b %d %H:%M:%S %Y')
                self.achieved = float(m1[0][1])
                self.ach_tol = float(m1[0][2])
                self.ach_dP = float(m1[0][3])
                self.vact = float(m1[0][4])
                self.gast = float(m1[0][5])
                # self.loop = float(m[0][6])

            mpat = re.compile(r"(.{24})(.{7})Up", re.MULTILINE | re.DOTALL | re.VERBOSE )
            m2 = re.findall(mpat, self.sdata)
            if m2 is not None:
                self.ts_stabinit = util.SDate2JavaMillis(m2[0][0], '%b %d %H:%M:%S %Y')

        except Exception as e :
            logger.debug('ScanDose failed interpret {} due {}'.format('teste', e.__repr__()))
