#! /usr/bin/env python3
"""
    Zikbox commands manager
"""
import sys
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
from os.path import expanduser

session = PromptSession(history = FileHistory(expanduser('~/.synth_history')))

class Commands(object):
    def __init__(self, *args, **kwargs):

        self.cmdDic = {
                "help": self.help, 
                "reset": self.reset, 
                "quit": self.quit,
                
                }


        self.cmdLst = self.cmdDic.keys()

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
                    self.cmdDic[func](*argLst[1:])
            else:
                print(f"{func}: Command not found.")

    #------------------------------------------------------------------------------
    
    def help(self, *args, **kwargs):
        print("Help...")

    #------------------------------------------------------------------------------
    
    def reset(self, *args, **kwargs):
        print("Reset...: ", args)

    #------------------------------------------------------------------------------
    
    def quit(self, *args, **kwargs):
        print("Bye!!!")
        sys.exit(0)

    #------------------------------------------------------------------------------
    
#========================================

def main():
    com = Commands()

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
