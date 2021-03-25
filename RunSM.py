import logging, re, os, sys, time
from threading import Thread, Timer
from pydispatch import dispatcher
from queue import Queue
# from itertools import izip

from BSP import SMStates, SIGNALS, ENTITIES

# from Topography import Topo
from IsthScanner import IsthScanner


logger = logging.getLogger(__name__)


class RunSM:


    def __init__(self, qlog, isthscanner):

        self.__signal = ""
        self.__running = True
        self.__signal_queue = Queue()

        self.isthscanner = isthscanner
        # self.bascon = bascon

        self.timerflag = False
        self.timer_reload = 0
        self.timer_counter = 0

        self.inactivity_period = 3000
        self.inactivity_taskperiod = 1.0
        self.inactivity_tick = 5.0
        self.inactivity_last = 0
        self.traffic_last = 0



        # ========= States management ================================
        self.smstates = SMStates()
        self.smstates.addState("INIT", 0, "ROOT")
        self.smstates.addState("CONFIG", 0, "ROOT")
        self.smstates.addState("IDLE", 0, "ROOT")

        self._states_lookup = {}
        self._states_lookup[self.smstates.sindex("INIT")] = self.init
        self._states_lookup[self.smstates.sindex("CONFIG")] = self.config
        self._states_lookup[self.smstates.sindex("IDLE")] = self.idle

        self._states_stack = list()
        self._states_stack.append(self.smstates.sindex("IDLE"))
        self._states_stack.append(self.smstates.sindex("CONFIG"))
        self._states_stack.append(self.smstates.sindex("INIT"))

        self.smstates.addState("LOAD_SCRIPT", 0, "ROOT")
        self._states_lookup[self.smstates.sindex("LOAD_SCRIPT")] = self.load_script

        self.smstates.addState("EVAL", 0, "ROOT")
        self._states_lookup[self.smstates.sindex("EVAL")] = self.eval_test

        self.smstates.addState("TIMER", 0, "ROOT")
        self._states_lookup[self.smstates.sindex("TIMER")] = self.set_timer

        self.configLogger(qlog)

        dispatcher.connect(self.runsm_dispatcher_receive, signal=SIGNALS.TERM_CMD, sender=dispatcher.Any)
        dispatcher.connect(self.runsm_dispatcher_quit, signal=SIGNALS.QUIT, sender=dispatcher.Any)
        dispatcher.connect(self.runsm_dispatcher_script, signal=SIGNALS.SCRIPT, sender=dispatcher.Any)
        dispatcher.connect(self.runsm_dispatcher_loadstate, signal=SIGNALS.LOADSTATE, sender=dispatcher.Any)


        self.isthscanner.addStates(self.smstates, self._states_lookup)
        # self.bascon.addStates(self.smstates, self._states_lookup)


    def runsm_dispatcher_loadstate(self, message):
        logger.debug('Signal loadstate with payload : {}'.format(message))
        self.push_cmd(message)

    def runsm_dispatcher_script(self, message):
        logger.debug('Signal Script with payload : {}'.format(message))
        self.execute_script(message)

    def runsm_dispatcher_receive(self, message):
        # logger.debug('Signal Received with payload : {}'.format(message))
        self.__signal_queue.put_nowait(message)

    def runsm_dispatcher_quit(self):
        self.__running = False
        # sys.exit()




    def go(self):

        logger.debug("This is the State Machine Manager - > Starting services...")
        t = Thread(target=self.runsm, args=())
        t.start();


    def configLogger(self, qlog):

        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(qlog)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(msecs).2f - %(levelno)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)


    def runsm(self):

        while self.__running:
            time.sleep(0.2)
            if self.timer_counter > 0:
                self.timer_counter -= 1
                if self.timer_counter % 10000 == 0:
                    dispatcher.send(message=" ", signal=SIGNALS.TERM_SHOWTIMER, sender=ENTITIES.RUNSM)
            else:
                # Execute @ states stack top
                if (self._states_stack.__len__()) == 0:
                    self.__running = False
                else:
                    # Do signal housekeeping
                    if not self.__signal_queue.empty():
                        self.__signal = self.__signal_queue.get()
                        self.push_cmd(self.__signal)

                    # Now execute the next cmd on line
                    state_index = self._states_stack.pop()
                    payload = self.smstates.getPayload(state_index)

                    states_to_load = self._states_lookup.get(state_index)(payload)
                    if states_to_load != None:
                        for lstate in states_to_load:
                            statereturn = self.smstates.sindex(lstate)
                            if statereturn != 2 :
                                logger.debug ('State returned : retrun ={} / lstate={} return={}\n\r'
                                       .format(statereturn, lstate, states_to_load))
                            self._states_stack.append(statereturn)

                if self.timer_reload != 0:
                    self.timer_counter = self.timer_reload



    def set_timer(self, payload):

        iterpl = iter(payload)
        cmds = dict(zip(iterpl, iterpl));
        # cmds = dict(map(None, *[iterpl] * 2))

        timer_clear = cmds.get("clear")
        timer_value = cmds.get("set")

        if timer_clear is not None:
            self.timer_reload = 0

        elif timer_value is not None:
            self.timer_reload = int(timer_value)
            self.do_timer();

        logger.debug('Timer set !')



    def inactivity_timer(self):

        # self.inactivity_tmr = Timer(self.inactivity_tick, self.inactivity_timer)
        # self.inactivity_tmr.start()

        imilli_string: object = os.popen("xprintidle").read()
        imillis = int(imilli_string)
        if imillis > self.inactivity_period :
            # Check for network activity ...
            ifconfig_string = os.popen("ifconfig eth6").read()
            regex = re.compile(r'(RX bytes.)(\d*\s)', re.MULTILINE)
            match = regex.search(ifconfig_string)
            if match:
                traffic = int(match.group(2))
                if self.inactivity_last == 0:
                    self.inactivity_last = traffic
                    delta_traffic = 0
                    logger.debug('Activity check = checking bandwidth...')
                    self.inactivity_tmr = Timer(1.0, self.inactivity_timer)
                    self.inactivity_tmr.start()
                else:
                    delta_traffic = traffic - self.inactivity_last
                    self.inactivity_last = traffic
                    if delta_traffic < 82000 :
                        logger.debug('Activity check = inactive @ {} - no network activity {}'
                                     .format (imillis, delta_traffic))
                        self.inactivity_tmr = Timer(1.0, self.inactivity_timer)
                        self.inactivity_tmr.start()
                        dispatcher.send(message='BASCON1 CHECK2 CHECK3',
                                        signal=SIGNALS.TERM_CMD,
                                        sender=ENTITIES.TERM)
                    else:
                        logger.debug('Activity check = inactive @ {} - but network activity -> {}'
                                     .format(imillis, delta_traffic))
                        self.inactivity_tmr = Timer(self.inactivity_tick, self.inactivity_timer)
                        self.inactivity_tmr.start()

        else:
            logger.debug('Activity check = active since {} millis'.format(imillis))
            self.inactivity_tmr = Timer(self.inactivity_tick, self.inactivity_timer)
            self.inactivity_tmr.start()




    def do_timer(self):

        self.tmr = Timer(self.timer_reload, self.do_timer)
        self.tmr.start()

        milliseconds_string = os.popen("xprintidle").read()
        seconds = int(milliseconds_string) / 1000

        logger.debug('Timer callback ! - idle = {}'.format(seconds))



    def get_signal_cmd(self, local_signal):

        vb_tokens = re.findall('\'\S*\'', local_signal)
        for token0 in vb_tokens:
            token1 = token0.replace('\'', '')
            token1 = token1.replace(' ', '|')
            token1 = token1.replace('=', '^')
            local_signal = local_signal.replace(token0, token1)

        tokens = re.split(r'[=\s]\s*', local_signal)

        for i in range(0, tokens.__len__()):
            tokens[i] = tokens[i].replace('|', ' ')
            tokens[i] = tokens[i].replace('^', '=')

        payload = tokens[1:]

        return tokens[0].upper(), payload



    def push_cmd(self, signal):
        cmd, payload = self.get_signal_cmd(signal)
        if self.smstates.sindex(cmd) in self._states_lookup:
            pstate = self.smstates.findState(cmd)
            if pstate != None:
                pstate.push_payload(payload)
            self._states_stack.append(self.smstates.sindex(cmd))
            # logger.debug("Valid Signal received : {}".format(cmd))
        else:
            logger.warn("Syntax Error : {}".format(cmd))





    # STATES ===========================================================================================================
    def init(self, payload):
        pass
        # logger.debug("Em Init State")

    def config(self, payload):
        # self.load_script(['./script1.txt'])
        #self.inactivity_timer()
        pass
        # logger.debug("Em Config State")

    def idle(self, payload):
        # self._states_stack.append(self.smstates.sindex("IDLE"))
        return ['IDLE']

    def execute_script(self, script_list, rv=True):
        #
        if rv == True:
            for line in reversed(script_list):
                self.push_cmd(line)
        else:
            for line in script_list:
                self.push_cmd(line)


    def load_script(self, payload):
        #
        cmds = list()
        if payload.__len__() == 0:
            logger.warning("Load from nothing ?")
        else:
            scriptpath = payload[0]
            logger.info("Loading script from file %s", scriptpath)
            file_obj = open(scriptpath, 'r')
            # script= ''.join(file_obj.readlines())
            lines = (line.strip() for line in file_obj)
            for line in lines:
                if line != "" and line[0] != "#":
                    logger.debug("Pushing cmd : {}".format(line))
                    cmds.append(line)

            if cmds:
                self.execute_script(cmds)
            file_obj.close()


    def eval_test(self, payload):

        iterpl = iter(payload)
        cmds = dict(zip(iterpl, iterpl));
        # cmds = dict(map(None, *[iterpl] * 2))

        slst = []
        slst.append("Evaluating command : \n\r")
        slst.append("=================================================================\n\r")
        for key, value in cmds.items():
            slst.append("\tKey {:<15} = {}\n\r".format(key, value))

        slst.append("=================================================================\n\r")
        logger.debug(''.join(slst))
