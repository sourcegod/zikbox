#! /usr/bin/env python3
"""
    Zikbox commands manager
"""
import sys
import midiman
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
from os.path import expanduser

session = PromptSession(history = FileHistory(expanduser('~/.synth_history')))

class Commands(object):
    def __init__(self, *args, **kwargs):

        self.cmdDic = {
                "help": self.help, 
                "quit": self.quit,
                "q": self.quit,
                "prog": self.prog,
                "bank": self.bank,
                "panic": self.panic, 
                "reset": self.reset, 
                "noteon": self.noteon,
                "noteoff": self.noteoff,
                "cc": self.cc,
                
                }


        self.cmdLst = self.cmdDic.keys()

    #------------------------------------------------------------------------------
    
    def init(self):   
        self.midman = midiman.MidiManager()
        self.midman.parent = self
        self.midman.init(driver=None, device=None, bank_file=None)
        self.midman.receive_from(port=1, callback=self.midman.input_callback)

    #------------------------------------------------------------------------------
    
    def close(self):
        self.midman.close()

    #------------------------------------------------------------------------------

    def search(self, *args, **kwargs):
        print(f"Searching: ", args)
        if args is not None: 
            # convert tuple to string and lowercase
            args = args[0].lower()
            argLst = args.split(' ')
            func = argLst[0] 
            if func in self.cmdLst:
                if len(argLst) == 1:
                    self.cmdDic[func]()
                else:
                    print("voici argLst: ", *argLst[1:])
                    self.cmdDic[func](*argLst[1:])
            else:
                print(f"{func}: Command not found.")

    #------------------------------------------------------------------------------
    
    def help(self, *args, **kwargs):
        print("Help...")

    #------------------------------------------------------------------------------
    
   
    def quit(self, *args, **kwargs):
        self.close()
        print("Bye!!!")
        sys.exit(0)

    #------------------------------------------------------------------------------
    
    def prog(self, chan, prg, *args, **kwargs):
        print("prog: ", chan, ":", prg)
        self.midman.program_change(chan, prg)

    #------------------------------------------------------------------------------

    def bank(self, chan, bnk, *args, **kwargs):
        self.midman.bank_change(chan, bnk)

    #------------------------------------------------------------------------------

    def panic(self, *args, **kwargs):
        self.midman.panic()

    #------------------------------------------------------------------------------

    def reset(self, *args, **kwargs):
        self.midman.panic()
        print("Reset...: ", args)

    #------------------------------------------------------------------------------
    
    def noteon(self, chan=1, note=60, vel=100, *args, **kwargs):
        self.midman.noteon(chan, note, vel)

    #------------------------------------------------------------------------------
 
    def noteoff(self, chan=1, note=60, *args, **kwargs):
        self.midman.noteoff(chan, note)

    #------------------------------------------------------------------------------
    
    def cc(self, chan=1, ctl=7, val=100, *args, **kwargs):
        print("ctl: ", repr(ctl), repr(val))
        self.midman.cc(chan, ctl, val)

    #------------------------------------------------------------------------------
  
#========================================

def main():
    com = Commands()
    com.init()

    while 1:
        val = session.prompt("-> ")
        # print(val)
        com.search(val)
        
        if val == "":
            print("No result")
            # sys.exit(0)

#------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------
