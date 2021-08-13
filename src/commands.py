#! /usr/bin/env python3
"""
    Zikbox commands manager
"""
import sys
import midiman
import utils
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
from os.path import expanduser

session = PromptSession(history = FileHistory(expanduser('~/.synth_history')))
def parseString(_str):
    """ 
    Warn: Inused
    Parse string and returns: list 
    """
    # Remove all spaces from string
    return _str.lower().split()
    
#------------------------------------------------------------------------------

class Commands(object):
    def __init__(self, *args, **kwargs):

        self.midman = midiman.MidiManager()
        self.midman.parent = self
        
        self._midiParamNames = (
                "chan", "key", "vel", 
                "_bank", "_prog", "val", "ctrl",
                )

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

        self.cmdDic = {
                "help": (self.help,  {}),
                "quit": (self.quit, {}),
                "q": (self.quit, {}),
                "prog": (self.midman.prog, self._progDic),
                "bank": (self.midman.bank, self._bankDic),
                "cc": (self.midman.cc, self._ccDic),
                "panic": (self.midman.panic,  {}),
                "reset": (self.midman.reset,  {}),
                
                "noteon": (self.midman.noteon, self._noteonDic),
                "noteoff": (self.midman.noteoff, self._noteoffDic),
                "note": (self.midman.note, self._noteDic),
                "bpm": (self.midman.bpm, {"val": 100}),
                "load": (self.midman.load, {"bankFile": None, "chan": 1}),
                "unload": (self.midman.unload, {}),
                "test": (self.midman.test, {"_prog": 16, "chan": 1}),
                "startsys": (self.midman.startsys, {}),
                "stopsys": (self.midman.stopsys, {}),
                
                }


        self.cmdLst = self.cmdDic.keys()
        self._midiFuncLst = ["prog", "bank", "cc",
                "noteon", "noteoff", "note", 
                "bpm", "load", "unload", "test",
                ]

    #------------------------------------------------------------------------------
    
    def init(self):   
        # self.midman = midiman.MidiManager()
        self.midman.init(driver=None, device=None, bank_file=None)
        self.midman.receive_from(port=1, callback=self.midman.input_callback)

    #------------------------------------------------------------------------------
    
    def close(self):
        self.midman.close()

    #------------------------------------------------------------------------------

    def makeDicParams(self, *args, **kwargs):
        """ 
        returns param's dictionnary of function 
        """

        argLen = len(args); kwargLen = len(kwargs)
        if len(args) > len(kwargs):
            print("Zikbox Warning: too many parameters")
        # construct dictionnary compréhension
        # {kwargs[k]=v for (k,v) in zip(kwargs.keys(), args)}
        for (i, item) in enumerate(kwargs.keys()):
            if i < argLen: 
                kwargs[item] =  args[i]
            else:
                break

        return kwargs

    #------------------------------------------------------------------------------

    def formatMidiParams(self, *args, **kwargs):
        """ 
        convert midi params to float 
        and returns: kwargs
        """
        
        for (key, val) in kwargs.items():
            if key in self._midiParamNames: 
                if not utils.is_number(val): 
                    return {}
                if isinstance(val, str) and val.isdigit():
                    kwargs[key] = int(val)
                elif isinstance(val, int):
                    kwargs[key] = val
                else:
                    # whether is a float, remove the zero after the dot
                    val = float(val)
                    if utils.is_int(val):
                        kwargs[key] = int(val)
                    else:
                        kwargs[key] = val

        return kwargs

    #------------------------------------------------------------------------------

    def limitMidiParams(self, funcName, *args, **kwargs):
        """ """
        # Warn: just for fun
        # limVal = lambda x, minVal=0, maxVal=127: minVal if x < minVal else maxVal if x > maxVal else x
        
        print(f"name: {funcName}")
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
                else:
                    kwargs[key] = utils.limit_value(int(val), 0, 127)
        
        print("result: ", kwargs)

        return kwargs
    
    #------------------------------------------------------------------------------

    def search(self, valStr):
        print(f"Searching: ", valStr)
        
        kwargDic = {}
        # Remove all spaces from string
        argLst = valStr.lower().split()
        if argLst:
            funcName = argLst.pop(0)
            if funcName in self.cmdLst:
                cmdFunc = self.cmdDic[funcName][0]
                kwargFunc = self.cmdDic[funcName][1]
                if kwargFunc:
                    # kwargDic = {k:v for (k, v) in zip(kwargFunc.keys(), argLst)}
                    kwargDic = self.makeDicParams(*argLst, **kwargFunc)
                if kwargDic: 
                    kwargDic = self.formatMidiParams(**kwargDic)
                    if not kwargDic:
                        print("Not check midi values")
                        return
                    kwargDic = self.limitMidiParams(funcName, **kwargDic)
                
                cmdFunc(**kwargDic)
            else:
                print(f"{funcName}: Command not found.")

    #------------------------------------------------------------------------------
    
    def help(self, *args, **kwargs):
        print("Help...")

    #------------------------------------------------------------------------------
    
   
    def quit(self, *args, **kwargs):
        self.close()
        print("Bye!!!")
        sys.exit(0)

    #------------------------------------------------------------------------------
    
#========================================

def main():
    com = Commands()
    com.init()

    while 1:
        valStr = session.prompt("-> ")
        # print(valStr)
        if valStr.lstrip() != "":
            com.search(valStr)
        else:
            print("No result")
            # sys.exit(0)

#------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------
