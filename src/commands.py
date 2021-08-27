#! /usr/bin/env python3
"""
    Zikbox commands manager
"""
import os
import sys
import midiman
import utils
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, PathCompleter

from os.path import expanduser
import curses
import asyncio
import threading
import readln

# globals variables
_DEBUG =0
_TRACING =0

_session = PromptSession(history = FileHistory(expanduser('~/.synth_history')))
_words_completer = WordCompleter(['prog', 'bank', 'note', 'noteon', 'noteoff', 'initmod', 'stopmod'])

_words_dic = { 
        'prog': ['_prog', '_chan'], 
        'bank': ['_bank', '_chan'], 
        'note': ['_key', '_vel', '_dur', '_chan'], 
        'noteon': ['_key', '_vel', '_chan'],
        'noteoff': ['_key', '_chan'],
        'demo': ['_prog', '_chan'],
        'initmod': ['_driv', '_dev', '_file'],
        'stopmod': [],
    }

class Commands(object):
    def __init__(self, *args, **kwargs):

        self.midman = midiman.MidiManager()
        self.midman.parent = self
        
        self._midiParamLst = [
                "chan", "key", "vel", 
                "_bank", "_prog", "val", "ctrl",
                ]

        self._progDic = {
                "_prog": 0, "chan": 1
                }

        self._bankDic = {
                "_bank": 0, "chan": 1
                }

        self._ccDic = {
                "ctrl": 0, "val": 0, "chan": 1
                }

        self._noteonDic = {
                "key": 60, "vel": 100, "chan": 1
                }

        self._noteoffDic = {
                "key": 60, "chan": 1
                }
        self._noteDic = {
                "key": 60, "vel": 100, "dur": 1, "chan": 1
                }

        self._helpDic = {
                "all": "Print all available helps",
                "help": "print this help",
                "test": "print about test command",
                "trace": "print about trace command",
                "quit": "Close the system",
                "about": "Zikbox Music System - Version 0.1",
                }

        self.globComDic = {
                "help": {"func": self.help, "help": "Short help on help", "all": self._helpDic["all"]},
                "quit": {"func": self.quit, },
                "q": {"func": self.quit, },
                "test": {"func": self.test, "_prog": 33, "chan": 1, },
                "trace": {"func": self.trace, },
                # "midport": {"func": self.midman.midport, "in": None, "out": None, "con": None, },
                
                }

       
        
        # """
        self._synthComDic = {
                "prog": {"func": self.midman.prog, **self._progDic}, 
                "bank": {"func": self.midman.bank, **self._bankDic},
                "cc": {"func": self.midman.cc, **self._ccDic},
                "panic": {"func": self.midman.panic,  },
                "reset": {"func": self.midman.reset,  },
                
                "noteon": {"func": self.midman.noteon, **self._noteonDic, },
                "noteoff": {"func": self.midman.noteoff, **self._noteoffDic, },
                "note": {"func": self.midman.note, **self._noteDic, },
                "bpm": {"func": self.midman.bpm, "val": 100, },
                "load": {"func": self.midman.load, "bankFile": None, "chan": 1, },
                "unload": {"func": self.midman.unload, },
                "demo": {"func": self.midman.demo, "_prog": 16, "chan": 1},
                "initmod": {"func": self.midman.initmod, "driver": None, "device": None, "bank_file": None, },
                "stopmod": {"func": self.midman.stopmod, },
                
                }
        # """

        
        self._midiFuncLst = ["prog", "bank", "cc",
                "noteon", "noteoff", "note", 
                "bpm", "load", "unload", "demo",
                # "test",
                ]

    #------------------------------------------------------------------------------
    
    def initApp(self):   
        # self.midman = midiman.MidiManager()
        # self.midman.parent = self
        self.midman.init(driver=None, device=None, bank_file=None)
        self.midman.receive_from(port=1)
        # st.s

    #------------------------------------------------------------------------------
    
    def close(self):
        self.midman.close()

    #------------------------------------------------------------------------------
    
    def mainWin(self):
        self.stdscr = curses.initscr()
        curses.noecho() # don't repeat key hit at the screen
        # curses.cbreak()
        # curses.raw() # for no interrupt mode like suspend, quit
        curses.start_color()
        curses.use_default_colors()
        self.ypos =0; self.xpos =0
        self.height, self.width = self.stdscr.getmaxyx()
        # initialize the main window
        self.win = curses.newwin(self.height, self.width, self.ypos, self.xpos)
        self.win.refresh()
        self.win.keypad(1) # allow to catch code of arrow keys and functions keys
        # self.win.nodelay(1)
    #------------------------------------------------------------------------------
    
    def main2(self):
        self.mainWin()
        self.initApp()
        self.keyHandler()

    #-------------------------------------------

    def keyHandler(self):
        msg = "Grovit Synth..."
        self.display(msg)
        curses.beep() # to test the nodelay function
        while 1:
            key = self.win.getch()
            if key >= 32 and key < 128:
                key = chr(key)
            if key == 'Q':
                self.close()
                self.win.close()
                break
        pass

    #-------------------------------------------


    def makeDicParams(self, *args, **kwargs):
        """ 
        create new dictionnary from a list and a dictionnary
        returns param's dictionnary of function 
        """

        # delete func key
        try:
            kwargs.pop("func")
        except KeyError:
            pass
        
        if len(args) > len(kwargs):
            print("Zikbox Warning: too many parameters")
        # construct dictionnary compréhension
        # Note: cannot using list comprehension to update dictionnary, 
        # cause no assignments in list comprehension, cause assignment is statement in python.
        for (k, v) in zip(kwargs.keys(), args):
            kwargs[k] = v
        if _TRACING:
            self.trace(title="makeDicParams", **kwargs)

        return kwargs

    #------------------------------------------------------------------------------

    def checkMidiParams(self, *args, **kwargs):
        isChan = lambda x: x.isdigit() and x >=0 and x <= 15
        isMidiVal = lambda x: x.isdigit() and x >=0 and x <= 127
        isBank = lambda x: x.isdigit() and x >=0 and x <= 16383
        isDur = lambda x: isInstance(x, (int, float)) and x >0
        isBpm = lambda x: isInstance(x, (int, float)) and x >0 and x <= 600
        
        funcLst = {
                (chan,): isChan,
                (note, key, vel, _prog, val, ctrl): isMidival,
                (bank,): isBank,
                (dur,): isDur,
                (bpm,): isBpm,

                }

        for (key, val) in kwargs.items():
            for item in funcDic.keys():
                if key in item:
                    print("here is key: ", key, "val: ", val)
                    if not funcDic[item](val): return False
            
            """
            if key == "chan":
                if not isChan(val): return False
            elif key in ("note", "key", "vel", "_prog", "val", "ctrl"):
                if not isMidiVal(val): return False
            elif key == "dur":
                if not isdur(val): return False
            elif key == "_bank":
                if not isBank(val): return False
            elif key == "bpm":
                if not isBpm(val): return False
                """
      
        return True

    #------------------------------------------------------------------------------

    def formatMidiParams(self, *args, **kwargs):
        """ 
        convert midi params to float 
        and returns: kwargs
        """
        
        for (key, val) in kwargs.items():
            if key in self._midiParamLst: 
                #if not utils.is_number(val):
                # Note: tips for determine whether string is int, float or string
                try:
                    float(val)
                except ValueError:
                    return {}
                
                val = float(val)
                if val.is_integer(): 
                    kwargs[key] = int(val)
                else:
                    kwargs[key] = val

        if _TRACING:
            self.trace(title="formatMidiParams", **kwargs)

        return kwargs

    #------------------------------------------------------------------------------

    def limitMidiParams(self, funcName, *args, **kwargs):
        """ """
        # Warn: just for fun
        # limVal = lambda x, minVal=0, maxVal=127: minVal if x < minVal else maxVal if x > maxVal else x
        
        # print(f"name: {funcName}")
        if funcName in self._midiFuncLst:
            for (key, val) in kwargs.items():
                # print(f"{key}: {val}")
                if funcName == "bpm":
                    kwargs[key] = utils.limit_value(float(val), 1, 600)
                    continue
               
                if funcName == "note" and key == "dur":
                    kwargs[key] = float(val)
                    continue

                # limit chan from 0 to 16
                if key == "chan":
                    val = utils.limit_value(int(val), 0, 16)
                    if val >0: val -=1
                    kwargs[key] = val 
                elif key == "_bank":
                    val = utils.limit_value(int(val), 0, 16384)
                    kwargs[key] = val 
                elif key == "bankFile":
                    val = str(val)
                    kwargs[key] = val 
                else:
                    kwargs[key] = utils.limit_value(int(val), 0, 127)
        
        # debugging
        # print("result: ", kwargs)
        if _TRACING:
            self.trace(title="limitMidiParams", **kwargs)

        return kwargs
    
    #------------------------------------------------------------------------------

    def parseString(self, valStr, *args):
        global _TRACING

        # print(f"Parsing: ", valStr)
        
        kwargDic = {}
        cmdFunc = None
        funcName = ""
        isGlob =1
        # Remove all spaces from string
        if valStr:
            argLst = valStr.lower().split()
        else:
            argLst = args
        if argLst:
            funcName = argLst.pop(0)
            
            if funcName in self.globComDic.keys():
                kwargDic = self.globComDic[funcName]
                cmdFunc = kwargDic["func"]
            elif funcName in self._synthComDic.keys():
                isGlob =0
                kwargDic = self._synthComDic[funcName]
                cmdFunc = kwargDic["func"]
                if kwargDic:
                    kwargDic = self.makeDicParams(*argLst, **kwargDic)
                if kwargDic: 
                    kwargDic = self.formatMidiParams(**kwargDic)
                    if not kwargDic:
                        self.display(title="Error", msg="Midi value not found")
                        return
                    else:
                        kwargDic = self.limitMidiParams(funcName, **kwargDic)
                
            else: # no funcname
                self.display(f"{funcName}: Command not found.")
                return

            if _TRACING:
                self.trace("parseString func", "", *argLst, **kwargDic)
            elif cmdFunc and isGlob:
                if funcName == "trace":
                    cmdFunc("parseString func", "", *argLst, **kwargDic)
                elif cmdFunc:
                    cmdFunc(*argLst, **kwargDic)
            else: # is not glob
                cmdFunc(**kwargDic)
        else: # is not arglst
            self.display(f"{funcName}: Command not found.")
        
        _TRACING =0
    #------------------------------------------------------------------------------
    
    def help(self, *args, **kwargs):
        print("Help...")
        # print(f"args: {args}\n kwargs: {kwargs}")
        if args:
            key = args[0]
            try:
                print(self._helpDic[key])
            except KeyError:
                print(f"{key}: no help for this keyword")
        else:
            print(self._helpDic["help"])

    #------------------------------------------------------------------------------
    
   
    def quit(self, *args, **kwargs):
        self.close()
        print("Bye!!!")
        sys.exit(0)

    #------------------------------------------------------------------------------
    
    def trace(self, title="", msg="", *args, **kwargs):
        global _TRACING
        print("Trace...")
        print(f"Title: {title}, msg: {msg}\n args: {args}, kwargs: {kwargs}")
        if args and args[0] == "trace":
            args = args.pop(0)
            _TRACING =1
            parseString(None, *args)

    #------------------------------------------------------------------------------

    async def asMain(self):
        # com = Commands()
        self.initApp()

        _session = PromptSession()
        while True:
            with patch_stdout():
                valStr = await _session.prompt_async("-> ", completer=_words_completer)
                # print(valStr)
                if valStr.lstrip() != "":
                    self.parseString(valStr)
                else:
                    # print("No result")
                    pass

    #------------------------------------------------------------------------------

    def display(self, msg="", title="[Ret]"):
        if title: 
            msg = f"{title}: {msg}"
        print(msg)
    
    #-------------------------------------------

   
    def main(self):
        # com = Commands()
        self.initApp()
        # Register our completer function
        readln.set_completer(_words_dic)
        readln.read_historyfile()
        try:
            while True:
                # valStr = _session.prompt("-> ", completer=_words_completer)
                # valStr = _session.prompt("-> ", completer=_path_completer)
                
                valStr = readln.get_input("-> ")
                # valStr = _session.prompt("-> ")
                # print(valStr)
                if valStr.lstrip() != "":
                    # print(f"Adding {valStr} to the history")
                    self.parseString(valStr)
                else:
                    print("No result")
                    pass

        finally:
            # print('Final history:', get_history_items())
            readln.write_historyfile()

    #------------------------------------------------------------------------------


    def test(self, *args, **kwargs):
        print("Test!!!")
        # print("Results", args, kwargs, sep="\n")
        self.midman.print_ports()

    #------------------------------------------------------------------------------
    
    
#========================================

if __name__ == "__main__":
    com = Commands()
    # app.main2()
    com.main()

#------------------------------------------------------------------------------
