
import Util as util

class JEntityCtrl(object):

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
            ch = ch.split('!')[1].strip()
            self.childrens[idx] = ch

        for idx,ch in enumerate(self.props):
            ch = ch.split('!')[1].strip()
            self.props[idx] = ch

        for idx,ch in enumerate(self.initvars):
            ch = ch.split('!')[1].strip()
            self.initvars[idx] = ch

        self.package = self.package.split('!')[1].strip()
        self.imports = self.imports.split('!')[1].strip()


    def getInitChildren(self):

        sb = util.StringBuilder('    ')
        for ci in self.childrens:
            citokens = ci.split('|')
            if len(citokens) == 2:
                sb+= 'private {} {}; '.format(citokens[1], citokens[0].lower()+'s')
            elif len(citokens) == 3:
                sb+= 'private {} {};'.format('Object', citokens[2] )
            else :
                sb+= 'private {} {};'.format('Object', citokens[0].lower())

            sb += '\n    '
        return str(sb)

    def getImports(self):

        sb = util.StringBuilder(self.imports)
        sb+='\n'
        for ci in self.childrens:
            citokens = ci.split('|')
            if len(citokens) > 1:
                sb+= 'import {}.{} ;'.format(self.package, citokens[0])
            else:
                sb+= 'import {}.{};'.format(self.package, citokens[0])
            sb += '\n'
        return str(sb)


    def getInitVars(self):

        sb = util.StringBuilder('    ')
        for ci in self.initvars:
            tokens = ci.split('|')
            sb+= 'private {} {} = {} ;\n'.format(
                                    tokens[1], tokens[0], '"'+tokens[2]+'"' if tokens[1]=="String" else tokens[2] )
            sb+= '    public {} get{}() {{ return {}; }}\n'.format(tokens[1], tokens[0].title(), tokens[0])
            sb+= '    public void set{}({} {}) {{ this.{} = {}; }}\n'.format(
                                     tokens[0].title(), tokens[1], tokens[0], tokens[0], tokens[0])

            sb += '\n    '

        return str(sb)


    def getRegistries(self, rtpl, lrtpl):

        sb = util.StringBuilder('    ')

        for ci in self.childrens:
            citokens = ci.split('|')
            if len(citokens) == 2: # List with init
                rtplh = lrtpl + " "
                chclass = citokens[0]
                child = '.' + citokens[0].lower()+'s'
                chinit = citokens[1]
            elif len(citokens) == 3: # Simple object with var name
                rtplh = rtpl + " "
                chclass = citokens[0]
                child = '.' + citokens[2]
                chinit = ''
            else : # Simple Object
                rtplh = rtpl + " "
                chclass = citokens[0]
                child = '.' + citokens[0].lower()
                chinit = ''

            rtplh = rtplh.replace('$RCHILDVAR', child)
            rtplh = rtplh.replace('$RCHILDCLASS', chclass)
            rtplh = rtplh.replace('$RCHILDINIT', chinit)

            sb += rtplh

        return str(sb)

    def getDBLinks(self):

        sbup = util.StringBuilder('')
        sbdown = util.StringBuilder('')

        sbup+='.append ("suid", suid )\n'
        sbup+='\t\t\t\t.append ("cascade", cascade )\n'

        sbdown+='\t\t_id = document.get("_id", ObjectId.class);\n'
        sbdown+='\t\tsuid = document.get("suid", Long.class);\n'
        sbdown+='\t\tcascade = document.get("cascade", Boolean.class);\n'


        for ci in self.childrens:
            citokens = ci.split('|')
            if len(citokens) == 2: # List with init
                varname = citokens[0].lower()+'s'
                sbup+='\t\t\t\t.append ("{}", get{}())\n'.format(varname, varname.capitalize())
                sbdown+='\t\t{} = document.get("{}", {}.class);\n'.format(varname, varname, 'ArrayList')
            elif len(citokens) == 3: # Simple object with var name
                varname = citokens[2].lower()
                sbup+='\t\t\t\t.append ("{}", ({} instanceof Long) ? {} : Long.parseLong({}.toString()) )\n' \
                    .format(varname, varname, varname, varname)
                sbdown+='\t\t{} = document.get("{}", Long.class);\n'.format(varname, varname)
            else : # Simple Object
                varname = citokens[0].lower()
                sbup+='\t\t\t\t.append ("{}", ({} instanceof Long) ? {} : Long.parseLong({}.toString()) )\n'\
                    .format(varname, varname, varname, varname)
                sbdown+='\t\t{} = document.get("{}", Long.class);\n'.format(varname, varname)

        for ci in self.initvars:
            tokens = ci.split('|')
            sbup+= '\t\t\t\t.append ("{}", {})\n'.format(tokens[0], tokens[0])
            sbdown+='\t\t{} = document.get("{}", {}.class);\n'.format(tokens[0], tokens[0], tokens[1])

        for prop in self.props :
            tokens = prop.split('|')
            sbup+= '\t\t\t\t.append ("{}", {})\n'.format(tokens[0], tokens[0])
            clazz = tokens[1] if 'ArrayList' not in tokens[1] else 'ArrayList'
            sbdown+='\t\t{} = document.get("{}", {}.class);\n'.format(tokens[0], tokens[0], clazz )

        return str(sbup) , str(sbdown)


    def getLoadChildren(self, rtpl, lrtpl ):

        sb = util.StringBuilder('    ')

        for ci in self.childrens:
            citokens = ci.split('|')
            if len(citokens) == 2: # List with init
                rtplh = lrtpl + " "
                chclass = citokens[0]
                child = citokens[0].lower()+'s'
                chinit = citokens[1]
            elif len(citokens) == 3: # Simple object with var name
                rtplh = rtpl + " "
                chclass = citokens[0]
                child = citokens[2]
                chinit = ''
            else : # Simple Object
                rtplh = rtpl + " "
                chclass = citokens[0]
                child = citokens[0].lower()
                chinit = ''

            rtplh = rtplh.replace('$CHILDVAR', child)
            rtplh = rtplh.replace('$CHILDCLASS', chclass)
            rtplh = rtplh.replace('$CHILDINIT', chinit)

            sb += rtplh

        return str(sb)

    def getServiceChildren(self, rtpl ):

        sb = util.StringBuilder('    ')

        for ci in self.childrens:
            citokens = ci.split('|')
            if len(citokens) == 2: # List with init
                rtplh = rtpl + " "
                chclass = citokens[0]
                child = citokens[0].lower()+'s'
                capchild = child.capitalize();

                rtplh = rtplh.replace('$CHILDVAR', child)
                rtplh = rtplh.replace('$CHILDCLASS', chclass)
                rtplh = rtplh.replace('$CAPCHILDVAR', capchild)

                sb += rtplh

        return str(sb)

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

    def getLinkChildrens(self):

        sb = util.StringBuilder('        ')

        for ci in self.childrens:

            sb+='self.'
            sb += ci.lower()
            sb += '.owner=self._id'
            sb += '\n        '

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

#
# public void loadChildren(boolean cascade){
#
#     EntityDescriptors ed = mongolink.getLoaded_descriptors();
#
# if (dose_pf instanceof Long){
#     Dose_pf dpf = (Dose_pf)ed.findById((Long)dose_pf, true);
# if (dpf != null) {
# dose_pf = dpf;
# if (cascade) dpf.loadChildren(cascade);
# }
# else{
#
# }
# }
#
# if (phases.get(0) instanceof Long){
# for (int i = 0; i < phases.size(); i++) {
# Long t_suid = (Long)phases.get(i);
# Phase t_phase = (Phase)ed.findById((Long)t_suid, true);
# if (t_phase != null) {
# phases.set(i, t_phase);
# //if (cascade) t_phase.loadChildren(cascade);
# }
# else{
#
# }
#
# }
#
# }
#
# }
