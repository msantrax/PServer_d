
import logging, re

from pydispatch import dispatcher
from BSP import SIGNALS, ENTITIES


logger = logging.getLogger(__name__)



class QCRImporter:

    filepath=''
    seed_datalist=list()
    sdata = ''

    regexes = {
        "ptrn_isothermpoints": re.compile(r"\\s{25}(.{11})\\s{36}(.{9})"),
        "ptrn_absolutepoints": re.compile(r"\\s{25}(.{11})\\s{36}(.{9})"),
        "ptrn_rawpoints": re.compile(r"\\s{25}(.{11})\\s{36}(.{9})"),

        "ptrn_operator": re.compile(r"Operator:(.{21})Date:(.{15}|.{10})"),
        "ptrn_sid": re.compile(r"Sample ID:(.{25})"),
        "ptrn_filename": re.compile(r"Filename:(.*)"),
        "ptrn_sdesc": re.compile(r"Sample Desc:(.{24})"),
        "ptrn_comment": re.compile(r"Comment:(.*)"),

        "smp_weight": re.compile(r"Sample weight:(.{21})"),
        "smp_volume": re.compile(r"Sample Volume:(.{21})"),
        "smp_density": re.compile(r"Sample Density:(.*)"),
        "outgas_time": re.compile(r"Outgas Time:(.{23})"),
        "outgas_temp": re.compile(r"OutgasTemp:(.*)")

    }


    def __init__(self, qlog, filepath = '/Bascon/ASVP/Quantawin/Data_190121/Seg3/sttn_A_20130206_1 (Isotherm).txt'):

        self.configLogger(qlog)
        self.filepath = filepath
        self.loadlog([filepath])
        self.scan()




    def loadlog(self, payload):

        if payload.__len__() == 0:
            logger.warning("setSource : Pointing to nothing ?")
        else:
            fpath = payload[0]
            logger.debug('QCRImporter Source pointing to : {}'.format(fpath))
            try:
                with open(fpath, 'rt') as fhandle:
                    self.sdata = fhandle.read()
                    self.filepath = fpath
                    self.seed_datalist = self.sdata.split('\n')
                    logger.debug('QCRScanner has loaded {} lines'.format(len(self.seed_datalist)))
                    fhandle.close()
            except Exception as e :
                logger.debug('QCRScanner failed to load file {} due {}'.format(fpath, e.__repr__()))

    def scan(self):

        try:
            m = re.findall(self.regexes["smp_weight"], self.sdata)
            if m is not None:
                res = m[0].replace('g', "")
                smp_weight = float(res)
                logger.debug('Found smp_weight = {}'.format(smp_weight))

            m = re.findall(self.regexes["smp_volume"], self.sdata)
            if m is not None:
                res = m[0].replace('cc', "")
                smp_volume = float(res)
                logger.debug('Found smp_volume = {}'.format(smp_volume))


        except Exception as e :
            logger.debug('QCRScanner failed interpret {} due {}'.format('teste', e.__repr__()))




    def configLogger(self, qlog=None):

        logger.setLevel(logging.DEBUG)

        if qlog is None:
            ch = logging.StreamHandler()
        else:
            ch = logging.StreamHandler(qlog)

        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


# (Saved)(.*?)(N320601.dat) - para separar pontos (não o primeiro)

# regexp -nocase -all -- {(.{24})TotalPntsReq=.*?DoseSta=(.{3}).*?atPoint=(.{2}).*?DoP0=(.{2}).*?P0SoFar=(.{2})} string match v1 v2 v3 v4 v5

# regexp -nocase -all -- {(.{24})VoidVolumeCell\[.\] =(.{8})} string match v1 v2 <-- VoidVolue

# (.{24})Build(.*?)(.{24})!A(.*?Up\]) -> separador de doses -> retorna segmento com dose

# regexp -nocase -all -- {(.{24})BuildPressure(.{7}).*?xover(.{7}).*?InitialP:(.{7})} string match v1 v2 v3 v4 <-- BuildPressure

# regexp -nocase -all -- {(.{24})Achieved: P(.{7}).*?tol(.{7})dP(.{7})Vact=(.{4})Gast=(.{3})loop=(.{2})} string match v1 v2 v3 v4 v5 v6 v7 <-- achieved

# regexp -nocase -all -- {(.{24})  \[STA t UP\]} string match v1 <-- STAUp single

# regexp -nocase -all -- {(.{24})  !A Redose in(.{3}).*?P2=(.{7})} string match v1 v2 v3 <- redose

# regexp -nocase -all -- {(.{24})  !A EQUILIBRIUM! Count =(.{4}).*?P =(.{7})} string match v1 v2 v3 <- Equilibrium





