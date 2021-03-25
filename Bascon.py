import logging, re
import shutil, os, glob
from fnmatch import fnmatch
import json
import uuid
import datetime


from pydispatch import dispatcher
from BSP import SMStates, SIGNALS, ENTITIES


logger = logging.getLogger(__name__)


class Bascon:

    def __init__(self, qlog):

        self.configLogger(qlog)

        self.workdir = '/Bascon/Books'
        self.temproot = '/Bascon/Bookstemp'
        self.setTempdir()

        self.worksubdirs = self.hasSubdirs (self.workdir)
        self. dirsize = self.getDirsize(self.workdir)


        # dirlist = os.listdir(self.workdir)

        # self.cleandir(self.tempdir)
        #
        # self.dirlist = os.listdir(self.workdir)
        #
        # for fname in self.dirlist:
        #
        #     cmd = 'md5sum "' + self.workdir+fname+'"'
        #     md5_str = str(os.popen(cmd).read())
        #     md5_str1 = md5_str[0:32]
        #     md5_num = int(md5_str1, 16)
        #     logger.debug('MD5 of file {} is {}'.format(fname, md5_num))
        #
        #
        # logger.debug('Bascon Manager Init @ {}'.format(self.workdir))

    def setTempdir(self):

        lpath = ''
        movres = ''

        self.tempdir = self.temproot + self.workdir

        if (os.path.isdir(self.tempdir)):
            if (self.getDirsize(self.tempdir)):
                logger.debug('Temp directory [{}] is not empty, moving payload to /bup and clearing'.format(self.tempdir))
                bupdir = self.temproot+'/bups/bup_'+ datetime.datetime.now().strftime("%d%m%y%H%M%S")
                os.makedirs(bupdir)
                lpath = 'rsync --remove-source-files -qa ' + self.tempdir + ' ' + bupdir
                rsyncout = str(os.popen(lpath).read())
                if ( rsyncout.__len__()) == 0:
                    lpath = 'rm -r ' + self.tempdir
                    rmout = str(os.popen(lpath).read())
                    if (rmout.__len__()) == 0:
                        os.makedirs(self.tempdir)
                        return True
                else:
                    logger.warning('Unable to move payload from tempdir :{}'.format(self.tempdir))
                    return False

        else:
            os.makedirs(self.tempdir)
            return True




    def cleandir (self, tempdir):

        try:
            os.makedirs(tempdir)
            pyfiles = [name for name in os.listdir(self.workdir) if
                       not (fnmatch(name, '*.pdf')) | fnmatch(name, '*.epub') | fnmatch(name, '*.pdf_1')
                       ]
            for fname in pyfiles:
                shutil.move(self.workdir + fname, self.tempdir)

        except Exception as a:
            logger.warning('Bypassing clean due -> {}'.format(a))



    def hasSubdirs (self, path):

        suffix = '*/' if path.endswith('/') else '/*/'
        lpath = 'ls -d ' + path + suffix
        subdirscan = str(os.popen(lpath).read())
        if (subdirscan).__len__() == 0:
            return
        else:
            subdirs = str(os.popen(lpath).read())
            lsubdirs = subdirs.split('\n')
            del lsubdirs[-1]
            return subdirs
        # return not(not subdirs)




    def getDirsize (self, path):

        dirsize = os.popen("du -Ss " + path).read()
        regex = re.compile(r'(\d*).('+ path + ')', re.MULTILINE)
        match = regex.search(dirsize)

        if match :
            size = match.group(1)
        else:
            size = -1

        return int(size)




    def configLogger(self, qlog):

        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(qlog)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


    def addStates(self, sm_states, states_lookup):

        sm_states.addState("BASCON1", 0, "BASCON")
        states_lookup[sm_states.sindex("BASCON1")] = self.bascon1
        sm_states.addState("BASCON2", 0, "BASCON")
        states_lookup[sm_states.sindex("BASCON2")] = self.bascon2
        sm_states.addState("BASCON3", 0, "BASCON")
        states_lookup[sm_states.sindex("BASCON3")] = self.bascon3

        sm_states.addState("BKSETSOURCE", 0, "BASCON")
        states_lookup[sm_states.sindex("BKSETSOURCE")] = self.setSource


#============================================== STATES ========================================================


    def bascon1(self, payload):

        logger.debug('On Bascon1 {}'.format(payload))
        return ['BASCON2', 'BASCON3']


    def bascon2(self, payload):
        logger.debug('On Bascon2 {}'.format(payload))


    def bascon3(self, payload):
        logger.debug('On Bascon3 {}'.format(payload))


    def setSource(self, payload):

        if payload.__len__() == 0:
            logger.warning("setSource : Pointing to nothing ?")
        else:
            self.workdir = payload[0]
            logger.debug('setSource pointing to : %s'.format(payload))
            self.worksubdirs = self.hasSubdirs(self.workdir)
            if (self.hassubdir):
                logger.debug('Source has subdirs')
            self.dirsize = self.getDirsize(self.workdir)
            logger.debug('Dir size is : %d', self.dirsize)

    def setTemp(self, payload):

        if payload.__len__() == 0:
            logger.warning("setTemp : Pointing to nothing ?")
        else:
            self.tempdir = payload
            logger.debug('setTemp pointing to : %s'.format(payload))



