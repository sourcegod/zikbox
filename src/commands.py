#! /usr/bin/env python3
"""
    Zikbox commands manager
"""
import sys

cmdDic = {
        "search", "help", "quit",
        
        }

class Commands(object):
    def __init(self, *args, **kwargs):
        pass

    #------------------------------------------------------------------------------
    
    def search(self, *args, **kwargs):
        print(f"Searching {args}...")

    #------------------------------------------------------------------------------
    
    def help(self, *args, **kwargs):
        print("Help...")

    #------------------------------------------------------------------------------
    
    def quit(self, *args, **kwargs):
        print("Bye!!!")

    #------------------------------------------------------------------------------
    
#========================================

def main():
    com = Commands()
    while 1:
        val = input("-> ")
        # print(val)
        com.search(val)
        
        if val == "quit":
            print("Bye!!!")
            sys.exit(0)

#------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
#------------------------------------------------------------------------------
