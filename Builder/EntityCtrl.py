
import Util as util

class EntityCtrl(object):

    # JSON Descriptor Default
    package = 'Entities.'
    classname = 'PropTest'
    initvars = ('owner|:str', 'index|int')
    props = ('init_ts:int', 'end_ts:int', 'test1:float')
    childrens = ('BuildPressure', 'CalcP0')
    # imports = ('import something from someplace\n', 'from somepackage import package\n')
    imports = ('')

    loadbody = ""
    parsebody = ""
    defaultbody = ""
    classbody = ""

    # End of Descriptor Default TODO : May be added dinamic ?

    def __init__(self):
        pass



    def prepareFields(self):

        for idx,ch in enumerate(self.childrens):
            ch = ch.split('!')[0].strip()
            self.childrens[idx] = ch

        for idx,ch in enumerate(self.props):
            ch = ch.split('!')[0].strip()
            self.props[idx] = ch

        for idx,ch in enumerate(self.initvars):
            ch = ch.split('!')[0].strip()
            self.initvars[idx] = ch

        self.package = self.package.split('!')[0].strip()

        self.imports = self.imports.split('!')[0].strip()

        pass


    def getChildrenImports(self):

        sb = util.StringBuilder('')
        for ci in self.childrens:
            if ':' in ci :
                citokens = ci.split(':')
                if citokens[1] in str(sb):
                    continue
                else:
                    ci = citokens[1]
            elif '|' in ci :
                citokens = ci.split('|')
                ci=citokens[0]

            sb += 'from '
            sb += self.package
            sb += ci
            sb += ' import '
            sb += ci
            sb += '\n'

        return str(sb)


    def getInitVars(self):

        sb = util.StringBuilder('    ')
        for ci in self.initvars:
            name, type = ci.split('|')
            sb += name
            if ':' in type :
                sb += ' '
                sb += type
            else:
                sb += ' = '
                sb += type
                # sb += '()'
            sb += '\n    '

        return str(sb)

    def getLinkChildrens(self):

        sb = util.StringBuilder('        ')

        for ci in self.childrens:

            sb+='self.'
            sb += ci.lower()
            sb += '.owner=self.suid'
            sb += '\n        '

        return str(sb)

    def getInitChildrens(self):

        sb = util.StringBuilder('    ')
        for ci in self.childrens:
            if ':' in ci :
                citokens = ci.split(':')
                sb += citokens[0].lower()
                sb += ' : '
                sb += citokens[1]
                sb += '\n    '
            elif '|' in ci :
                citokens = ci.split('|')
                sb += citokens[2]
                sb += ' : '
                sb += citokens[1]
                sb += '\n    '
            else:
                sb += ci.lower()
                sb += ' : '
                sb += ci
                sb += '\n    '

        return str(sb)

    def getRegistries(self, rtpl, lrtpl):

        sb = util.StringBuilder('    ')

        for ci in self.childrens:
            if ':' in ci :
                citokens = ci.split(':')
                ci=citokens[0]
                ciclass = citokens[1]
                rtplh = rtpl+" "
            elif '|' in ci :
                citokens = ci.split('|')
                ci=citokens[2]
                ciclass = citokens[0]
                rtplh = lrtpl+" "
            else:
                ciclass = ci
                rtplh = rtpl+" "

            child = '.'+ ci.lower()
            rtplh = rtplh.replace('$RCHILDVAR', child)
            rtplh = rtplh.replace('$RCHILDCLASS', ciclass)

            sb += rtplh

        return str(sb)

    def getChildrenMethods(self, rtpl, lrtpl):

        sb = util.StringBuilder('    ')
        sb1 = util.StringBuilder('')
        if self.childrens :
            sb1 += '    def loadChildrens(self, mongolink=None):\n'


        for ci in self.childrens:

            if ':' in ci :
                citokens = ci.split(':')
                ci=citokens[0]
                ciclass = citokens[1]
                rtplh = rtpl+" "
            elif '|' in ci :
                citokens = ci.split('|')
                ci=citokens[0]
                ciclass = citokens[0]
                rtplh = lrtpl+" "
            else:
                ciclass = ci
                rtplh = rtpl+" "

            collection = ci.lower()
            if '_' in ci :
                if not '_pf' in ci :
                    ctokens = ci.split('_')
                    collection = ctokens[1]

            rtplh = rtplh.replace('$CHILDVAR', ci.lower())
            rtplh = rtplh.replace('$CHILDCLASS', ciclass)
            rtplh = rtplh.replace('$LOADCHILDREN', 'True')
            rtplh = rtplh.replace('$CLASSNAME', self.classname)
            rtplh = rtplh.replace('$COLLECTION', collection)

            sb1 += '        self.load'+ci.lower()+'(mongolink)\n'
            sb += rtplh

        return str(sb1), str(sb)
