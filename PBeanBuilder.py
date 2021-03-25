
import re, time, os, shutil
import Util as util
from Util import StringBuilder

import logging
logger = logging.getLogger(__name__)

import jsons, json

from Builder.EntityCtrl import EntityCtrl


class PBeanBuilder(object):

    slices = {}
    segments = {}
    builder_path = '/Bascon/ASVP/PSERVER/Sandbox/PServer_d/Builder/'
    entities_path = '/Bascon/ASVP/PSERVER/Sandbox/PServer_d/Entities/'

    previous = None

    tpl_handle = None
    ctrl = None

    def __init__(self, qlog=None):
        logger = self.configLogger()


    def loadTemplate(self, entity='BuildPressure'):

        try:
            with open(self.builder_path + 'Entity.tpl', 'rt') as fhandle:
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

            self.ctrl = util.loadJson(self.builder_path + entity + '.json', EntityCtrl)

            fpath = self.entities_path + self.ctrl.classname + '.py'
            if os.path.exists(fpath):
                with open(fpath, 'rt') as fhandle:
                    self.previous = fhandle.read()
                    fhandle.close()

            self.build()

        except Exception as e :
            logger.debug('PBeanBuilder failed to load file {} due {}'.format(entity, e.__repr__()))


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

        # self.ctrl = Entityctrl()
        # util.saveJson(self.ctrl, self.root_path + recipe)

        self.ctrl.prepareFields()

        outfile = self.ctrl.classname+'.py'
        sb = StringBuilder('')

        try:

            stmp = self.slices['IMPORTSYS']
            stmp = stmp.replace('$IMPORTS', ''.join(self.ctrl.imports))
            sb += stmp

            stmp = self.slices['SUPER']
            stmp = stmp.replace('$PACKAGE', self.ctrl.package)
            sb += stmp

            stmp = self.slices['CHILDRENS']
            stmp = stmp.replace('$CHILDRENS', self.ctrl.getChildrenImports())
            sb += stmp

            stmp = self.slices['LOGGING']
            sb += stmp

            stmp = self.slices['CLASSDEF']
            stmp = stmp.replace('$CLASSNAME', self.ctrl.classname)
            sb += stmp

            stmp = self.slices['INITVARS']
            stmp = stmp.replace('$INITVARS', self.ctrl.getInitVars())
            sb += stmp

            stmp = self.slices['INITCHILDRENS']
            stmp = stmp.replace('$CHILDINITS', self.ctrl.getInitChildrens())
            sb += stmp

            psb = StringBuilder('')
            for prop in self.ctrl.props :
                name, type = prop.split(':')
                stmp = self.slices['PROPERTY']
                stmp = stmp.replace('$NAME', name)
                stmp = stmp.replace('$TYPE', type)
                psb += stmp

            spsb = str(psb)
            stmp = self.slices['PROPERTIES']
            stmp = stmp.replace('$PROPERTIES', spsb)
            sb += stmp

            stmp = self.slices['CONSTRUCTOR']
            stmp = stmp.replace('$CLASSNAME', self.ctrl.classname)
            # stmp = stmp.replace('$LINKCHILDRENS', self.ctrl.getLinkChildrens())
            sb += stmp

            stmp = self.slices['BASEMETHODS']
            stmp = stmp.replace('$CLASSNAME', self.ctrl.classname)

            stmp = stmp.replace('$LOADBODY', self.getsegment(self.ctrl.loadbody, 'LOAD'))
            stmp = stmp.replace('$PARSEBODY', self.getsegment(self.ctrl.parsebody, 'PARSE'))
            stmp = stmp.replace('$DEFAULTBODY', self.getsegment(self.ctrl.defaultbody, 'DEFAULT'))

            stmp = stmp.replace('$COLLECTION', self.ctrl.classname.lower())
            stmp = stmp.replace('$REGISTRIES', self.ctrl.getRegistries(self.slices['REGISTRY'],
                                                                       self.slices['REGISTRYLIST']))
            sb += stmp

            stmp = self.slices['CHILDRENLOAD']
            calls, methods = self.ctrl.getChildrenMethods(self.slices['CHILDRENLOADMETHOD'],
                                                          self.slices['CHILDRENLOADLISTMETHOD'])

            stmp = stmp.replace('$LOADMETHODS', methods)
            stmp = stmp.replace('$LOADCALLS', calls)
            sb += stmp

            stmp = self.slices['CLASSMETHODS']
            stmp = stmp.replace('$CMETHODS', self.getsegment(self.ctrl.classbody, 'CLASS'))
            sb += stmp

            sout = str(sb)

            with open(self.entities_path + outfile, 'wt') as fhandle:
                fhandle.write(sout)
                fhandle.close()

            util.logger.debug('PBeanBuilder sucessfully built {}'.format(outfile))
            # logger.logger.debug('PBeanBuilder sucessfully built {}'.format(outfile))

        except Exception as e:
            logger.debug('PBeanBuilder failed to save cleaned file {} due {}'.format(outfile, e.__repr__()))


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


