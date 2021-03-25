import locale
import curses
import logging, time, os, subprocess, re, sys
from threading import Thread, Event
from queue import Queue

from pydispatch import dispatcher

from BSP import SMStates, SIGNALS, ENTITIES

class CTerm:

    running = True
    padlines = 0
    wpos = 0
    padcursor = 0
    cursorx = 0
    cursory = 0
    bounce = 0
    indent = 0

    prompt = ""
    prompt_cursor = 0
    PROMPT_DEFAULT = " Anfitria : "
    prompt_header= PROMPT_DEFAULT
    prompt_header_lenght=0
    prompt_space=0

    prompt_timerchar = ['|', '/', '-', '\\', '|', '/', '-', '\\']
    prompt_timerchar_ptr = 0;

    _LOG_HISTORY = 2000

    _in_queue = Queue()

    _cmd_history = list()
    _cmd_history_ptr = 0
    _cmd_history_tail = 0

    _localcmd_lookup = {}

    _history_file = "./history.txt"


    def __init__(self):

        try:

            locale.setlocale(locale.LC_ALL, '')

            self.stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(1)

            self.theight, self.twidth = self.stdscr.getmaxyx()

            self.set_prompt_header()
            self.promptwin = curses.newwin(1, self.twidth, self.theight-1, 0)
            self.promptwin.keypad(1)
            self.promptwin.timeout(100)
            self.draw_prompt()

            self.logwin = curses.newpad(self._LOG_HISTORY, self.twidth)

            self.term_println("=========================================================")
            self.term_println("    Terminal VServer -- Core Python 3.6", curses.A_BOLD)
            self.term_println("=========================================================")

            self._localcmd_lookup['CLS']= self.clear_canvas
            self._localcmd_lookup['CLEAR_HISTORY'] = self.clear_history
            self._localcmd_lookup['EDIT_FILE'] = self.edit_file
            self._localcmd_lookup['RESET'] = self.reset_term
            self._localcmd_lookup['TEST'] = self.term_test
            self._localcmd_lookup['QUIT'] = self.quit_term
            self._localcmd_lookup['INFO'] = self.show_info

            dispatcher.connect(self.dispatcher_writeln, signal=SIGNALS.TERM_WRITELINE, sender=dispatcher.Any)
            dispatcher.connect(self.show_timer, signal=SIGNALS.TERM_SHOWTIMER, sender=dispatcher.Any)

            self.load_history("")

        except Exception as e:
            self.stdscr.keypad(0)
            curses.echo();
            curses.nocbreak()
            curses.endwin()
            print (e)

    def show_timer(self):

        if self.prompt_timerchar_ptr > 6 :
            self.prompt_timerchar_ptr = 0
        else:
            self.prompt_timerchar_ptr +=1

        c = self.prompt_timerchar[self.prompt_timerchar_ptr]
        self.promptwin.addch(0, 0, c, curses.A_BOLD)
        self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)


    def set_prompt_header(self, mes = " Anfitria : "):

        self.prompt_header = mes
        self.prompt_header_lenght = self.prompt_header.__len__()
        self.prompt_space = self.twidth - self.prompt_header_lenght

    def term_test(self):
        for i in range(0, 210):
            self.term_println("line {} @ ptr {}".format(i, self.padlines))


    def dispatcher_writeln(self, message):
        self.term_println('Signal Received with payload : {}'.format(message))

    def reset_term(self, lpayload):
        self.term_println('Reseting term ...')
        self.draw_prompt(True)

    def quit_term(self, lpayload):
        self.running = False
        self.exit_term()


    def exit_term(self):

        self.save_history("")

        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

        dispatcher.send(message="",
                        signal=SIGNALS.QUIT,
                        sender=ENTITIES.TERM)

    def go(self):
        t = Thread(target=self.mainloop, args=(self._in_queue,))
        t.start()

    def set_signal_queue(self, signal_queue):
        self._out_queue = signal_queue

    def mainloop (self, in_q):
        time.sleep(1)
        while self.term_key_handler():
            if  not in_q.empty():
                data = in_q.get()
                self.term_println(data)
                # self.term_refresh()
                self.promptwin.refresh()

        self.exit_term()

    def get_inqueue(self):
        return self._in_queue


    def term_key_handler(self):

        if not self.running:
            return 0

        c = self.promptwin.getch()

        # if c == ord(']'):
        if c == curses.KEY_END :
            return 0
        elif c == -1:
            return 1
        elif c == curses.KEY_F2:
            if self.padcursor > 0:
                self.padcursor -= 1
                self.term_refresh()
            return 1
        elif c == curses.KEY_F3:
            if self.padcursor < self.padlines:
                self.padcursor += 1
                self.term_refresh()
            return 1
        elif c == curses.KEY_LEFT:
            if self.prompt_cursor > 0:
                self.prompt_cursor -=1
                self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)
            return 1
        elif c == curses.KEY_RIGHT:
            pcur = len(self.prompt)
            if self.prompt_cursor < pcur:
                self.prompt_cursor +=1
                self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)
            return 1

        elif c == curses.KEY_UP:
            if self._cmd_history_ptr > 0:
                self._cmd_history_ptr -= 1
                self.prompt = self._cmd_history[self._cmd_history_ptr]
                self.draw_prompt()
                pass
            return 1
        elif c == curses.KEY_DOWN:
            if  (self._cmd_history.__len__() -1) > self._cmd_history_ptr:
                self._cmd_history_ptr +=1
                self.prompt=self._cmd_history[self._cmd_history_ptr]
                self.draw_prompt()
                pass
            return 1

        elif (c == curses.KEY_BACKSPACE) or (c == 127):
            if self.prompt_cursor > 0:
                sleft = self.prompt[:self.prompt_cursor-1]
                sright = self.prompt[self.prompt_cursor:]
                self.prompt = sleft + sright
                self.prompt_cursor -= 1
                self.promptwin.clrtoeol()
                self.promptwin.addstr(0, self.prompt_header_lenght, self.prompt + ' ', curses.A_BOLD)
                self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)
                # self.promptwin.insch(0, self.prompt_cursor + 11, ' ')
            return 1

        elif c == curses.KEY_ENTER or c == 10 or c == 13:
            if self.bounce != 10:

                if self.prompt !='':
                    if type(self.prompt) is not str :
                        self.prompt = self.prompt.decode('utf-8')
                    temp_prompt = self.prompt.upper()
                    cmd , payload = self.get_signal_cmd(self.prompt)
                    # Verify if it is local command
                    if cmd in self._localcmd_lookup:
                        temp1 = self._localcmd_lookup.get(temp_prompt)
                        temp1(payload)
                    else:
                        dispatcher.send(message=self.prompt,
                                        signal=SIGNALS.TERM_CMD,
                                        sender=ENTITIES.TERM)
                    if self.prompt not in self._cmd_history:
                        self._cmd_history.append(self.prompt)
                        self._cmd_history_tail +=1
                        self._cmd_history_ptr +=1

                self.term_println(self.prompt_header + self.prompt, curses.A_BOLD)

                self.prompt = ''
                self.prompt_cursor=0
                self.draw_prompt()
                self.bounce = c

            else:
                self.bounce=0
            return 1

        else:
            if self.prompt_cursor == self.prompt.__len__():
                self.promptwin.insch(0, self.prompt_cursor + self.prompt_header_lenght, c, curses.A_BOLD)
                self.prompt_cursor += 1
                self.prompt = self.promptwin.instr(0, self.prompt_header_lenght, self.prompt_cursor)
                self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)
            else:
                sleft = self.prompt[:self.prompt_cursor]
                sright = self.prompt[self.prompt_cursor:]
                self.prompt = "{0}{1:c}{2}".format(sleft, c, sright)
                self.prompt_cursor +=1
                self.promptwin.addstr(0, 0, self.prompt_header + self.prompt, curses.A_BOLD)
                self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)

            return 1

    def term_refresh(self):
        if self.padlines < self.theight:
            self.logwin.refresh(0, 0, 0, 0, self.theight-2, self.twidth - 1)
            # self.draw_prompt()
        else:
            self.logwin.refresh((self.padlines+2)-self.theight, 0, 0, 0, self.theight-2, self.twidth-1)
        #     # self.draw_prompt()

    def term_print(self, tstring, tattr):
        self.logwin.addstr(tstring, tattr)
        self.cursory, self.cursorx = self.logwin.getyx()

    def term_println(self, tstring, tattr=curses.A_NORMAL):

        pcy, pcx = self.logwin.getyx()

        if self.padlines >= self._LOG_HISTORY:
            self.cursory = 0
            self.padlines = 0
            self.padcursor = 0
            self.logwin.erase()

        self.logwin.addstr(self.cursory, self.indent, tstring, tattr)
        self.cursory, self.cursorx = self.logwin.getyx()

        self.cursory += 1
        self.padlines += self.cursory-(pcy+1)
        self.padcursor += self.cursory-(pcy+1)

        # if self.padlines < self._LOG_HISTORY-1:
        #     self.logwin.addstr(self.cursory, 0, tstring, tattr)
        #     self.cursory, self.cursorx = self.logwin.getyx()
        #
        # else:
        #     # self.logwin.scroll()
        #     self.cursory = 0
        #     self.logwin.addstr(self.cursory, 0, tstring, tattr)
        #     self.padlines +=1
        #     self.padcursor = 23

        self.term_refresh()


    #----------------------------------------------------------------------------------------------
    # local command services
    def draw_prompt(self, full=True):

        self.promptwin.clear()

        pcrop = self.prompt.__len__() - self.prompt_space
        if (pcrop > 0):
            prompt = self.prompt[pcrop+1:]
        else:
            prompt=self.prompt

        self.promptwin.addstr(0, 0, self.prompt_header + prompt, curses.A_BOLD)
        self.prompt_cursor = prompt.__len__()
        self.promptwin.move(0, self.prompt_cursor + self.prompt_header_lenght)
        self.promptwin.refresh()


    def clear_canvas(self, lpayload):

        self.logwin.erase()
        self.cursory = 0
        self.padlines = 0
        self.padcursor = 0
        self.logwin.move(0, 0)
        self.term_refresh()
        # self.cursory, self.cursorx = self.logwin.getyx()

    def load_history(self, lpayload):
        if os.path.exists(self._history_file):
            self.term_println("Loading command history")
            with open(self._history_file, 'rt') as f:
                for line in f:
                    line=line.strip('\n')
                    line=line.strip('\r')
                    self._cmd_history.append(line)
                    self._cmd_history_ptr += 1
                    self._cmd_history_tail += 1
        else:
            self.term_println("History file doesn't exists")

    def save_history(self, lpayload):
        with open(self._history_file, 'wt') as f:
            f.writelines( list( "%s\r\n" % item for item in self._cmd_history) )

    def clear_history(self, lpaylaod):
        self._cmd_history= list()
        self._cmd_history_ptr = 0
        self._cmd_history_tail = 0
        self.term_println("History was cleared")

    def edit_file(self, lpayload):
        self.stdscr.keypad(0)
        curses.echo();
        curses.nocbreak()
        curses.endwin()
        subprocess.call(["nano", "./history.txt"])
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        self.load_history()


    def show_info(self, lpayload):

        # self.indent = 10
        self.term_println("\n\rTerminal Info : ")
        self.term_println("======================================================")
        self.term_println("Terminal size = {} X {}".format(self.theight, self.twidth))
        self.term_println("Log Cursor {:d} ".format(self.padlines))

        self.term_println("\n\r")
        # self.indent = 0



    # ----------------------------------------------------------------------------------------------
    # Utilities
    def get_signal_cmd(self, local_signal):

        vb_tokens = re.findall('\'\w*\'', local_signal)
        for token0 in vb_tokens:
            token1 = token0.replace('\'', '')
            token1 = token1.replace(' ', '|')
            local_signal = local_signal.replace(token0, token1)

        tokens = re.split(r'[=\s]\s*', local_signal)

        for i in range(0, tokens.__len__()):
            tokens[i] = tokens[i].replace('|', ' ')

        payload = tokens[1:]

        return tokens[0].upper(), payload

