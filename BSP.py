class SIGNALS(list):
    GEN, \
    LOG, \
    QUIT, \
    TERM_WRITELINE, \
    TERM_SHOWTIMER, \
    TERM_CMD, \
    LOADSTATE, \
    SCRIPT, \
    GATEVENT,\
    ENTITYCHANGE \
    = range(10)

class ENTITIES(list):
    TERM, \
    ROOT, \
    TORNADO, \
    RUNSM, \
    UDPGATE, \
    ISTHSCANNER,\
    MONGOLINK, \
    ENTITY \
    = range(8)


class SMStates:

    # Loads a HTML Code from a resource
    def __init__(self):
        self.states = list()
        self.realms = list()
        self.lastindex = 0


    def addState(self, name, index, realm):

        if index == 0:
            self.states.append(SMState(name, self.lastindex, realm))
            self.lastindex +=1
        else:
            self.states.append(SMState(name, index, realm))
            self.lastindex = index

        if realm not in self.realms:
            self.realms.append(realm)

    def sindex (self, name):
        for tstate in self.states:
            if tstate.sname == name:
                return tstate.sindex
        return -1

    def findState(self, name):
        for rstate in self.states:
            if rstate.sname == name:
                return rstate
        return None

    def getPayload(self, index):
        st_payload = self.states[index].pop_payload()
        #self.states[index].payload = ''
        return st_payload


class SMState :

    #
    def __init__(self, state_name , state_index, realm):
        self.sname = state_name
        self.sindex = state_index
        self.realm = realm
        self.payloads = [" "]

    @property
    def index (self, state_name):
        return self._sindex

    def push_payload(self, payload):
        self.payloads.append(payload)

    def pop_payload(self):
        if self.payloads :
            return self.payloads.pop()
        else :
            return None

