#! /usr/bin/env python3
"""
    Zikbox commands manager
"""
import sys

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
            argLst = args[0].split(' ')
            func = argLst[0] 
            if func in self.cmdLst:
                if len(argLst) == 1:
                    self.cmdDic[func]()
                else:
                    self.cmdDic[func](*argLst[1:])
            else:
                print("Command not found.")

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
        val = input("-> ")
        # print(val)
        com.search(val)
        
        if val == "":
            print("No result")
            # sys.exit(0)

#------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------
