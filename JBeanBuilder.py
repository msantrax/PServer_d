
import re, time, os, shutil
import Util as util
from Util import StringBuilder

import logging
logger = logging.getLogger(__name__)

import jsons, json

from Builder.JEntityCtrl import JEntityCtrl


class JBeanBuilder(object):

    slices = {}
    segments = {}
    builder_path = '/Bascon/ASVP/PSERVER/Sandbox/PServer_d/Builder/'
    # entities_path = '/Bascon/ASVP/PSERVER/Sandbox/PServer_d/Entities/'
    entities_path = '/Bascon/ASVP/ASVP_ANA/Sandbox/MiddleStripB/src/Entities/'

    previous = None

    tpl_handle = None
    ctrl = None

    def __init__(self, qlog=None):
        logger = self.configLogger()

    def loadTemplate(self, entity='Isotherm'):

        try:
            with open(self.builder_path + 'JEntity.tpl', 'rt') as fhandle:
                data = fhandle.read()
                fhandle.close()
                self.buildSlices(data, self.slices)


            # Load template or the seed ?
            fpath = self.builder_path + entity + '.tpl'
            if not os.path.exists(fpath):
                shutil.copy(self.builder_path + 'ClassNameSeed.tpl', fpath)

            with open(self.builder_path + entity + '.tpl', 'rt') as fhandle:
                data = fhandle.read()
                fhandle.close()
                self.buildSlices(data, self.segments)

            self.ctrl = util.loadJson(self.builder_path + entity + '.json', JEntityCtrl)

            fpath = self.entities_path + self.ctrl.classname + '.java'
            if os.path.exists(fpath):
                with open(fpath, 'rt') as fhandle:
                    self.previous = fhandle.read()
                    fhandle.close()

            self.build()

        except Exception as e :
            logger.debug('JBeanBuilder failed to load file {} due {}'.format(entity, e.__repr__()))


    def buildSlices (self, data, dest):

        try:
            mpat0 = re.compile(r'&\[\w*\]', re.MULTILINE | re.DOTALL | re.VERBOSE)
            m = re.findall(mpat0, data)
            if m is not None:
                for slice in m :
                    slice = slice.translate({ord('&'):None, ord('['):None, ord(']'):None})
                    mpat = re.compile(r'(&\[{}\])(.*)(\[{}\]&)'.format(slice, slice), re.MULTILINE | re.DOTALL | re.VERBOSE)
                    m = re.search(mpat, data)
                    if m is not None:
                        dest.update({slice : m.group(2)})
                        # logger.debug('Loading slice {}'.format(m.group(2)))

        except Exception as e :
            logger.debug('PBeanBuilder failed to parse {} due {}'.format(slice, e.__repr__()))


    def getsegment (self, key, pointer):

        if '#segment' in key :
            return self.segments[pointer]
        else:
            if self.previous is None:
                return self.segments[pointer]
            else:
                pointer = pointer.lower()
                mpat0 = re.compile(r'(\#{}code_begin)(.*)(\#{}code_end)'.format(pointer, pointer), re.MULTILINE | re.DOTALL | re.VERBOSE)
                m = re.search(mpat0, self.previous)
                if m is not None:
                    return m.group()
                else:
                    return key



    def build (self):


        self.ctrl.prepareFields()

        outfile = self.ctrl.classname+'.java'
        sb = StringBuilder('')


        try:


            stmp = self.slices['PACKAGE']
            stmp = stmp.replace('$PACKAGE', self.ctrl.package)
            sb += stmp

            stmp = self.slices['IMPORTS']
            stmp = stmp.replace('$IMPORTS', self.ctrl.getImports())
            sb += stmp

            stmp = self.slices['CLASSDEF']
            stmp = stmp.replace('$CLASSNAME', self.ctrl.classname)
            sb += stmp


            stmp = self.slices['INITCHILDRENS']
            stmp = stmp.replace('$CHILDINITS', self.ctrl.getInitChildren())
            sb += stmp

            stmp = self.slices['INITVARS']
            stmp = stmp.replace('$INITVARS', self.ctrl.getInitVars())
            sb += stmp


            # Properties
            psb = StringBuilder('')
            for prop in self.ctrl.props :
                tokens = prop.split('|')
                stmp = self.slices['PROPERTY']
                stmp = stmp.replace('$NAME', tokens[0])
                stmp = stmp.replace('$TYPE', tokens[1])
                stmp = stmp.replace('$VALUE','"'+tokens[2]+'"' if tokens[1]=="String" else tokens[2] )

                if tokens[3] is "":
                    stmp = stmp.replace('$PROPERTYLINK', '')
                else:
                    outstr = '@propertylink (propname = PROP_{}, plink = "it_{}", input={}, callstate="{}")'.format(
                                                        tokens[0].upper(),
                                                        tokens[0],
                                                        tokens[4],
                                                        tokens[5],
                    )
                    stmp = stmp.replace('$PROPERTYLINK', outstr)

                stmp = stmp.replace('$UPNAME', tokens[0].upper())
                stmp = stmp.replace('$CAPNAME', tokens[0].title())
                psb += stmp


            spsb = str(psb)
            stmp = self.slices['PROPERTIES']
            stmp = stmp.replace('$PROPERTIES', spsb)
            sb += stmp

            stmp = self.slices['CONSTRUCTOR']
            stmp = stmp.replace('$CLASSNAME', self.ctrl.classname)
            stmp = stmp.replace('$COLLECTION', self.ctrl.classname.lower())
            stmp = stmp.replace('$REGISTRIES', self.ctrl.getRegistries(self.slices['REGISTRY'],
                                                                       self.slices['REGISTRYLIST']))
            sb += stmp

            stmp = self.slices['LOADCHILDREN']
            stmp = stmp.replace('$CHILDRENCLASS', self.ctrl.classname)
            stmp = stmp.replace('$LOADCHILDREN', self.ctrl.getLoadChildren( self.slices['LOADCHILD'],
                                                                            self.slices['LOADLISTCHILD']))
            sb += stmp

            stmp = self.slices['DBLINK']
            sbup, sbdown = self.ctrl.getDBLinks()
            stmp = stmp.replace('$DBUPLINKS', sbup)
            stmp = stmp.replace('$DBDOWNLINKS', sbdown)
            sb += stmp

            stmp = self.slices['SERVICECHILDREN']
            stmp = stmp.replace('$SERVICECHILDREN', self.ctrl.getServiceChildren(self.slices['SERVICECHILD']))
            sb += stmp


            stmp = self.slices['CLASSMETHODS']
            stmp = stmp.replace('$CMETHODS', self.getsegment(self.ctrl.classbody, 'CLASS'))
            sb += stmp

            sout = str(sb)

            sout = sout.replace('#class', '//class')

            with open(self.entities_path + outfile, 'wt') as fhandle:
                fhandle.write(sout)
                fhandle.close()

            util.logger.debug('JBeanBuilder sucessfully built {}'.format(outfile))
            # logger.logger.debug('PBeanBuilder sucessfully built {}'.format(outfile))

        except Exception as e:
            logger.debug('JBeanBuilder failed to save cleaned file {} due {}'.format(outfile, e.__repr__()))


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




    # initial = 'value \n\r'
    # stringBuilder = StringBuilder(initial)
    # for _ in range(5):
    #     stringBuilder += 'value \n\r'
    # for ind in range(5):
    #     stringBuilder.appendind('indent\n\r', ind)\
    #                  .appendind('second\n\r', ind)
    #
    # logger.debug('String Builder did : {}'.format(str(stringBuilder)))


