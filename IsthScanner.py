import logging, re

from pydispatch import dispatcher
from BSP import SIGNALS, ENTITIES

from Entities.CalcP0 import CalcP0



logger = logging.getLogger(__name__)


class IsthScanner:

    def __init__(self, qlog):

        self.configLogger(qlog)
        self.filepath=''

        self.seed_datalist=[]
        self.clean_ph1 = list()
        self.clean_ph2 = list()

        self.presurize_ph = list()
        # self.calcp0_ph = list()

        self.zerotdc1_ph = list()
        self.zerotdc2_ph = list()

        self.cp0 = CalcP0()





    def go(self):

        logger.debug("This is the Isotherm log Scanner --> ready to analyse")
        self.loadlog (['/Bascon/ASVP/Research/analise1.log', True])


    def configLogger(self, qlog):

        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(qlog)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


    def addStates(self, sm_states, states_lookup):

        sm_states.addState("LOADLOG", 0, "ISTHSCANNER")
        states_lookup[sm_states.sindex("LOADLOG")] = self.loadlog

        sm_states.addState("CLEANP1", 0, "ISTHSCANNER")
        states_lookup[sm_states.sindex("CLEANP1")] = self.clean_phase1

        sm_states.addState("CLEANP2", 0, "ISTHSCANNER")
        states_lookup[sm_states.sindex("CLEANP2")] = self.clean_phase2



#============================================== STATES ========================================================

    def loadlog(self, payload):

        if payload.__len__() == 0:
            logger.warning("setSource : Pointing to nothing ?")
        else:
            fpath = payload[0]
            logger.debug('IsthScanner Source pointing to : {}'.format(fpath))
            try:
                with open(fpath, 'rt') as fhandle:
                    data = fhandle.read()
                    self.filepath = fpath
                    self.seed_datalist = data.split('\n')
                    logger.debug('IsthScanner has loaded {} lines'.format(len(self.seed_datalist)))
                    fhandle.close()
                    if payload[1] :
                        # logger.debug('Request to clean is {}'.format(payload[1]))
                        dispatcher.send(message='CLEANP2', signal=SIGNALS.LOADSTATE, sender=ENTITIES.ISTHSCANNER)
                        dispatcher.send(message='CLEANP1', signal=SIGNALS.LOADSTATE, sender=ENTITIES.ISTHSCANNER)


            except Exception as e :
                logger.debug('IsthScanner failed to load file {} due {}'.format(fpath, e.__repr__()))



    def clean_phase1(self, payload):

        linecount = 0
        exclude = re.compile(r'Received|Saving|Save|Deleted')
        outpath = '/Bascon/ASVP/Research/analise1_clean_phase1.log'

        for line in self.seed_datalist:
            linecount = linecount+1
            if line =="" :
                continue
            if exclude.match(line):
                # logger.debug('Excluding {} @ line {}'.format(line, linecount))
                continue

            self.clean_ph1.append(line)

        try:
            with open(outpath, 'wt') as fhandle:
                for outline in self.clean_ph1:
                    fhandle.write(outline + "\n")
                fhandle.close()

        except Exception as e:
            logger.debug('IsthScanner failed to save cleaned file {} due {}'.format(outpath, e.__repr__()))

        logger.debug('IsthScanner cleaned by phase 1, now we have {} lines'.format(len(self.clean_ph1)))



    def clean_phase2(self, payload):

        i = 0;
        exclude = re.compile(r'Received|Saving|Save|Deleted|Using C')
        outpath = '/Bascon/ASVP/Research/analise1_clean_phase2.log'

        ph1size = len(self.clean_ph1)
        while i < ph1size :
            line = self.clean_ph1[i]
            if line.startswith('Pressurizing'):
                self.presurize_ph = self.clean_ph1[i:i + 5]
                i = i+5
                logger.debug('IsthScanner clean phase 2 registered pressurizing -> {} \n'.format(self.presurize_ph))
            elif line.startswith('Analyzing') or line.startswith('Preparing'):
                i+=1
                continue
            elif line.startswith('Calculating P0'):
                # self.calcp0_ph = self.clean_ph1[i:i + 6]
                self.cp0.load(self.clean_ph1[i:i + 6])
                self.cp0.parse()
                i = i + 6
                logger.debug('IsthScanner clean phase 2 registered Calcp0 -> {} \n'.format(self.calcp0_ph))
            elif line.startswith('Zeroing Transducer...'):
                self.calcp0_ph = self.clean_ph1[i:i + 6]
                i = i + 6
                logger.debug('IsthScanner clean phase 2 registered Calcp0 -> {} \n'.format(self.calcp0_ph))


            else:
                i += 1
                self.clean_ph2.append(line)

        try:
            with open(outpath, 'wt') as fhandle:
                for outline in self.clean_ph2:
                    fhandle.write(outline + "\n")
                fhandle.close()

        except Exception as e:
            logger.debug('IsthScanner failed to save phase 2 cleaned file {} due {}'.format(outpath, e.__repr__()))

        logger.debug('IsthScanner cleaned by phase 2, now we have {} lines'.format(len(self.clean_ph2)))


    def set_pressurizing(self, lnumber):

        tlist = self.clean_ph1[lnumber:lnumber + 5]

        for line in tlist:
            line +='\n'
            self.presurize_ph += line;
        logger.debug('IsthScanner clena phase 2 registered pressurizing -> {}'.format(self.presurize_ph))
        return 5

    def set_calcp0(self, lnumber):

        self.calcp0_ph.join(self.clean_ph1[lnumber:lnumber + 6])
        logger.debug('IsthScanner clena phase 2 registered Calcp0 -> {}'.format(self.calcpo_ph))
        return 6
